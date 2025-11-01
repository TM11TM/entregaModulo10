from langchain_qdrant import QdrantVectorStore
from src.services.embeddings import embeddings_model_langchain

### LANGCHAIN
qdrant_langchain = QdrantVectorStore.from_existing_collection(
    embedding=embeddings_model_langchain, # Los usa internamente la BBDD
    collection_name="langchain_index_bge",
    url="http://localhost:6333",
)