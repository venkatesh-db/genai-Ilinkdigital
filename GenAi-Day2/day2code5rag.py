
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

# -----------------------
# Step 1: Load Documents
# -----------------------
loader = TextLoader("sample.txt")
docs = loader.load()

# -----------------------
# Step 2: Split Documents
# -----------------------
splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# -----------------------
# Step 3: Embeddings + FAISS
# -----------------------
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(chunks, embeddings)

# -----------------------
# Step 4: Manual similarity search
# -----------------------
query = "Summarize this document."
relevant_docs = vectorstore.similarity_search(query, k=3)  # k = top 3 docs
context = "\n".join([d.page_content for d in relevant_docs])

# -----------------------
# Step 5: Call OpenAI directly
# -----------------------
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Answer this based on context:\n{context}\nQuestion: {query}"}
    ]
)

answer = response.choices[0].message.content
print("Answer:", answer)
