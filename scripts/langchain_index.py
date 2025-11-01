import sys
import os , time
from dotenv import load_dotenv
sys.path.append('.')
load_dotenv()
from qdrant_client import QdrantClient
from langchain_community.document_loaders import PyPDFDirectoryLoader
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff
from langchain_qdrant import QdrantVectorStore
from src.services.embeddings import embeddings_model_langchain
from uuid import uuid4
from datetime import datetime

DATA_PATH = 'data/optimized_chunks'
COLLECTION_NAME = "langchain_index_bge"
QDRANT_URL = "http://localhost:6333"
QDRANT_GRPC_PORT = 6334
BATCH_SIZE = 20
SLEEP_TIME = 45 
EMBEDDING_DIMENSION = 1024 

# Load
loader = PyPDFDirectoryLoader(DATA_PATH)
documents = loader.load()

for doc in documents:
    source_path = doc.metadata.get('source','')
    file_name = os.path.basename(source_path)
    source_name = os.path.splitext(file_name)[0]
    # Atributos adicionales
    doc.metadata['source'] = source_name
    doc.metadata['category'] = 'BOE actual'
    doc.metadata['processed_date'] = datetime.now().strftime('%Y-%m-%d')
    doc.metadata['status'] = 'active'  # Para gestión de obsolescencia
    doc.metadata['version'] = 'v1.0'
    
# Cargar los documentos en Qdrant usando Langchain 
# Usamos VectorStore de Langchain para gestionar la carga de documentos
# Manera rapida solo con un pdf
# QdrantVectorStore.from_documents(
#     collection_name=collection_name,
#     embedding=embeddings_model_langchain,
#     documents=documents,
#     url="http://localhost:6333",
#     prefer_grpc=True,
#     force_recreate=True,
# )

# Para procesar varios pdfs no podemos usar QdrantVectorStore.from_documents
# porque no podemos intrducirle time.sleep para el error 429
client = QdrantClient(
    url=QDRANT_URL,
    grpc_port=QDRANT_GRPC_PORT,
    prefer_grpc=True,
    timeout=60  # Timeout más largo para operaciones grandes
)

try:
    client.get_collection(COLLECTION_NAME)
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_DIMENSION,  # 768 para Gemini text-embedding-004
        distance=Distance.COSINE,   # Mejor para embeddings normalizados
        hnsw_config=HnswConfigDiff(
            m=16,               # Conexiones por nodo (16-64 recomendado)
            ef_construct=100,   # Precisión durante construcción (100-200)
            full_scan_threshold=10000,  # Usar brute-force si < 10K docs
        )
    ),
    optimizers_config={
        "indexing_threshold": 20000,  # Crear índice después de 20K puntos
    })

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings_model_langchain,
)

# Función batch
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

for doc_batch in batch(documents, BATCH_SIZE):
    ids = [str(uuid4()) for _ in doc_batch]
    vector_store.add_documents(documents=doc_batch, ids=ids)
    print(f'Batch of {len(doc_batch)} documents processed.')
    time.sleep(50)

print("All documents processed.")

