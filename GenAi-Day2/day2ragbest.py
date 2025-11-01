
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# ================================
# STEP 1: Load your compliance documents
# ================================

documents = [
    """
    Environmental Compliance Report 2024:
    The Clean Water Act mandates safe disposal of industrial waste.
    Companies must ensure that water discharge meets safety standards under Section 21.
    Violation leads to penalties under the Environmental Protection Act.
    """,
    """
    India’s Environmental Regulations:
    Air and water pollution control must align with CPCB (Central Pollution Control Board) guidelines.
    Industries near rivers must perform quarterly water safety tests and submit reports to the State Board.
    """,
    """
    Renewable Energy Compliance:
    Every power plant above 50MW must include solar integration and meet emission thresholds.
    The Ministry of Environment audits such plants every fiscal year.
    """
]

# ================================
# STEP 2: Chunking (Split text into small retrievable parts)
# ================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,
    chunk_overlap=50,
)
chunks = []
for doc in documents:
    chunks.extend(text_splitter.split_text(doc))

print(f"✅ Total Chunks Created: {len(chunks)}")

# ================================
# STEP 3: Create Embeddings and Vector Store
# ================================

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_texts(chunks, embeddings)

# ================================
# STEP 4: Setup Retriever (Hybrid Search)
# ================================

retriever = vectorstore.as_retriever(
    search_type="mmr",  # "similarity" or "mmr" (hybrid: balances diversity + relevance)
    search_kwargs={"k": 3}
)

# ================================
# STEP 5: Define Prompt Template
# ================================

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are an environmental compliance assistant.\n"
        "Use the context below to answer accurately:\n\n"
        "{context}\n\n"
        "Question: {question}\n"
        "Answer in clear, regulatory terms."
    )
)

# ================================
# STEP 6: Build RAG Chain
# ================================

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",   # simplest way to stuff context into prompt
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt_template},
)

# ================================
# STEP 7: Ask a Question
# ================================

query = "What are the water safety regulations in India?"
response = rag_chain.invoke({"query": query})

print("\n🧠 Query:", query)
print("\n📄 Answer:", response["result"])
