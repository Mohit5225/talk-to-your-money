import os
from dotenv import load_dotenv
import qdrant_client
from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import Settings
from qdrant_client.http.models import VectorParams, Distance


# --- 1. Load Environment Variables ---
load_dotenv()


# --- 2. Initialize Qdrant Client ---
client = qdrant_client.QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


# --- 3. Create or Reset Collection ---
collection_name = "talk_to_your_money"


if client.collection_exists(collection_name):
    client.delete_collection(collection_name)


client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)


# --- 4. Set Google Embedding Model for LlamaIndex ---
Settings.embed_model = GoogleGenAIEmbedding(
    model="text-embedding-004",  # ✅ Current embedding model
    api_key=os.getenv("GOOGLE_API_KEY")
)


# --- 5. Create LlamaIndex Vector Store ---
vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# --- 6. Mock Data & Indexing Function ---
def setup_and_test_rag():
    print("Setting up RAG and running a test...")


    # Mock documents
    mock_data_texts = [
        "In August 2025, the total spending for the 'food' category was $450.32.",
        "In August 2025, the total spending for the 'transportation' category was $120.15.",
        "On 2025-08-15, a transaction of $12.50 was made for 'Netflix Subscription' under the entertainment category.",
        "On 2025-08-20, a transaction of $85.00 was made for 'New Shoes' under the shopping category."
    ]
    documents = [Document(text=t) for t in mock_data_texts]


    # Create Vector Index
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)


    # Initialize Google LLM with current model
    gemini_llm = GoogleGenAI(
        api_key=os.getenv("GOOGLE_API_KEY"), 
        model="gemini-2.5-flash"  # ✅ Current working model
    )
    query_engine = index.as_query_engine(llm=gemini_llm)


    # Test Query 1
    response1 = query_engine.query("How much did I spend on food in August?")
    print("\n--- Test Query 1 ---")
    print("Question: How much did I spend on food in August?")
    print(f"Answer: {response1}")


    # Test Query 2
    response2 = query_engine.query("What was the transaction for new shoes?")
    print("\n--- Test Query 2 ---")
    print("Question: What was the transaction for new shoes?")
    print(f"Answer: {response2}")


    print("\nSetup and test complete.")


# --- Main Execution ---
if __name__ == "__main__":
    setup_and_test_rag()
