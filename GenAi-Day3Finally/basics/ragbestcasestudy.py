
"""
rag_pipeline.py — Retrieval-Augmented Generation (RAG) example
Compatible with: langchain==1.0.3, langchain-core==1.0.2, langchain-openai==1.0.1

Features:
- Chunking (RecursiveCharacterTextSplitter)
- FAISS vector store for embeddings
- Hybrid retrieval: semantic (vector) + keyword boost
- RetrievalQA chain (LLM uses retrieved context)
- Simple caching/fallback and logging
"""

import logging
from typing import List, Tuple
from dataclasses import dataclass
import re

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import os

# ---------- logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---------- sample documents (replace with your real docs) ----------
DOCUMENTS = [
    """
    Environmental Compliance Report 2024:
    The Clean Water Act mandates safe disposal of industrial waste.
    Companies must ensure that water discharge meets safety standards under Section 21.
    Violation leads to penalties under the Environmental Protection Act.
    """,
    """
    India’s Environmental Regulations:
    Air and water pollution control must align with CPCB guidelines.
    Industries near rivers must perform quarterly water safety tests and submit reports to the State Board.
    """,
    """
    Renewable Energy Compliance:
    Every power plant above 50MW must include solar integration and meet emission thresholds.
    The Ministry of Environment audits such plants every fiscal year.
    """,
    # Add large docs here...
]

# ---------- config ----------
EMBEDDING_MODEL = "text-embedding-3-small"   # OpenAI embeddings model (langchain-openai)
LLM_MODEL = "gpt-4o-mini"                    # LLM used for final generation
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
TOP_K_SEMANTIC = 4       # number of semantic neighbors to retrieve
TOP_K_KEYWORD = 6        # used for keyword scanning
KEYWORD_BOOST = 1.5      # factor to increase score for keyword presence


# ---------- helpers & hybrid retriever ----------
@dataclass
class RetrievedDoc:
    text: str
    score: float
    source: str = "semantic"   # semantic or keyword or mixed

def clean_text(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()

def build_vectorstore(docs: List[str], embeddings: OpenAIEmbeddings) -> FAISS:
    """Chunk docs and build FAISS vector store (in-memory)."""
    logging.info("Splitting documents into chunks (chunk_size=%s, overlap=%s)", CHUNK_SIZE, CHUNK_OVERLAP)
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    raw_chunks = []
    for i, d in enumerate(docs):
        chunks = splitter.split_text(d)
        for c in chunks:
            raw_chunks.append(clean_text(c))
    logging.info("Total chunks created: %d", len(raw_chunks))

    logging.info("Creating FAISS vector store (this will compute embeddings)...")
    vectorstore = FAISS.from_texts(raw_chunks, embeddings)
    
    # Store the raw chunks for keyword search
    vectorstore.raw_chunks = raw_chunks
    return vectorstore

def hybrid_retrieve(query: str, vectorstore: FAISS, top_k_semantic: int = TOP_K_SEMANTIC,
                    top_k_keyword: int = TOP_K_KEYWORD, keyword_boost: float = KEYWORD_BOOST) -> List[RetrievedDoc]:
    """
    Hybrid retrieval strategy:
      1) Semantic neighbors from FAISS (top_k_semantic)
      2) Keyword scan among chunks (simple substring match) to boost relevance
      3) Merge and re-score: semantic score (distance->score), add boost for keyword matches
    """
    logging.info("Hybrid retrieve for query: %s", query)
    try:
        # 1) semantic retrieval (returns (text, score) pairs from FAISS)
        semantic_results = vectorstore.similarity_search_with_score(query, k=top_k_semantic)
    except Exception as e:
        logging.error("Semantic retrieval failed: %s", e)
        semantic_results = []

    retrieved = []
    # convert semantic results to RetrievedDoc
    for doc, score in semantic_results:
        # FAISS returns cosine distance-like values; convert to similarity score (larger is better)
        # Here we invert/normalize by using 1/(1+score) as a quick transform. Adjust as needed.
        sim_score = 1.0 / (1.0 + (score if isinstance(score, (int, float)) else 0.0))
        text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
        retrieved.append(RetrievedDoc(text=text, score=sim_score, source="semantic"))

    # 2) simple keyword scan on all stored texts
    # get all texts from our stored raw_chunks
    all_texts = getattr(vectorstore, 'raw_chunks', [])
    if not all_texts:
        # Fallback: try to get from docstore if available
        try:
            all_texts = [doc.page_content for doc in vectorstore.similarity_search("", k=100)]
        except:
            all_texts = []
    q_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    keyword_matches = []
    for t in all_texts:
        tlow = t.lower()
        match_count = sum(1 for term in q_terms if term in tlow)
        if match_count > 0:
            # naive keyword score: match_count / number_of_terms
            score = match_count / (len(q_terms) + 0.0001)
            keyword_matches.append((t, score))

    # sort keyword matches and take top_k_keyword
    keyword_matches.sort(key=lambda x: x[1], reverse=True)
    for text, kscore in keyword_matches[:top_k_keyword]:
        # if already present from semantic retrieval, boost that entry
        existing = next((r for r in retrieved if r.text == text), None)
        if existing:
            existing.score = existing.score * (1.0 + (keyword_boost * kscore))
            existing.source = "mixed"
        else:
            retrieved.append(RetrievedDoc(text=text, score=kscore * keyword_boost, source="keyword"))

    # final sort by score desc and return
    retrieved.sort(key=lambda r: r.score, reverse=True)
    logging.info("Hybrid retrieved %d candidates", len(retrieved))
    return retrieved

# ---------- build RAG system ----------
def build_rag_system(vectorstore: FAISS, llm: ChatOpenAI):
    """
    Build simple RAG system that uses vectorstore and LLM directly.
    Returns a function that can answer questions using retrieved context.
    """
    def answer_question(query: str, context: str) -> str:
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are an expert environmental compliance assistant. Use only the provided context to answer the question.\n\n"
                "Context:\n{context}\n\nQuestion: {question}\n\nAnswer concisely and cite the most relevant points from the context."
            ),
        )
        
        formatted_prompt = prompt_template.format(context=context, question=query)
        response = llm.invoke(formatted_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    return answer_question

# ---------- main demo ----------
def main():
    print("🔍 Advanced RAG System - Environmental Compliance Assistant")
    print("=" * 65)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        print("🎭 Demo Mode: Showing RAG system structure...")
        
        print(f"\n📚 Sample Documents: {len(DOCUMENTS)} environmental compliance docs")
        print(f"🔧 Configuration:")
        print(f"   - Embedding Model: {EMBEDDING_MODEL}")
        print(f"   - LLM Model: {LLM_MODEL}")
        print(f"   - Chunk Size: {CHUNK_SIZE}")
        print(f"   - Semantic Results: {TOP_K_SEMANTIC}")
        print(f"   - Keyword Results: {TOP_K_KEYWORD}")
        
        print(f"\n📝 Sample Queries:")
        queries = [
            "What are the water safety regulations in India?",
            "Which power plants require solar integration?",
            "How often should industries near rivers test water quality?"
        ]
        for i, q in enumerate(queries, 1):
            print(f"   {i}. {q}")
        
        print(f"\n💡 To run full RAG system:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # 1) prepare embeddings & LLM
        logging.info("Initializing embeddings and LLM...")
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        llm = ChatOpenAI(model=LLM_MODEL, temperature=0.2)

        # 2) build vectorstore (chunking + embeddings)
        vectorstore = build_vectorstore(DOCUMENTS, embeddings)

        # 3) build RAG system
        rag_qa_function = build_rag_system(vectorstore, llm)

        # 4) user queries (demo)
        queries = [
            "What are the water safety regulations in India?",
            "Which power plants require solar integration?",
            "How often should industries near rivers test water quality?"
        ]
        
        print(f"\n🚀 Processing {len(queries)} queries...")
        print("=" * 65)

        for q in queries:
            try:
                logging.info("Processing query: %s", q)

                # hybrid retrieve
                candidates = hybrid_retrieve(q, vectorstore, top_k_semantic=TOP_K_SEMANTIC,
                                             top_k_keyword=TOP_K_KEYWORD, keyword_boost=KEYWORD_BOOST)

                # assemble top-k context (dedup, keep best N)
                seen = set()
                context_parts = []
                for r in candidates[:6]:   # include up to 6 chunks as context
                    # Handle RetrievedDoc objects
                    if hasattr(r, 'text'):
                        txt = r.text.strip()
                    elif hasattr(r, 'page_content'):
                        txt = r.page_content.strip()
                    else:
                        txt = str(r).strip()
                        
                    if txt not in seen:
                        context_parts.append(txt)
                        seen.add(txt)

                if not context_parts:
                    logging.warning("No context retrieved; using direct vectorstore search.")
                    # Fallback: use vectorstore directly for semantic search
                    fallback_docs = vectorstore.similarity_search(q, k=2)
                    fallback_context = "\n\n---\n\n".join([doc.page_content for doc in fallback_docs if hasattr(doc, 'page_content')])
                    answer = rag_qa_function(q, fallback_context)
                    print(f"\n🔍 Q: {q}")
                    print(f"📋 A (fallback): {answer}")
                    continue

                # create the final prompt context (join carefully to avoid token bloat)
                context = "\n\n---\n\n".join(context_parts)

                # call the RAG system with assembled context
                try:
                    answer = rag_qa_function(q, context)
                except Exception as e:
                    logging.error("RAG system failed: %s", e)
                    answer = "Sorry, I encountered an error processing this query."

                print(f"\n🔍 Q: {q}")
                print(f"📋 A: {answer}")
                
            except Exception as e:
                import traceback
                print(f"\n❌ Error processing query '{q}': {e}")
                traceback.print_exc()
                print("This might be due to API key issues, missing dependencies, or network problems.")
                # Simple fallback
                answer = f"Unable to process query due to error: {str(e)}"

            print(f"\n🔍 Q: {q}")
            print(f"📋 A: {answer}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might be due to API key issues, missing dependencies, or network problems.")

if __name__ == "__main__":
    main()
