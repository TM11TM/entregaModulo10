from fastapi import APIRouter, Query

from src.api.schema import RAGRequest
from src.process_langchain.chain import rag_chain
from src.services.vector_store import qdrant_langchain

router = APIRouter()

@router.post("/rag")
async def rag_endpoint(request: RAGRequest):
    """
    Endpoint to interact with the RAG system.
    """
    result = await rag_chain.ainvoke({"question": request.question})
    return {
        "question": result["question"],
        "answer": result["answer"],
        "source": result["source"].selection if result.get('source') else None,
        "source_reason": result["source"].reason if result.get('source') else None
    }

@router.get("/search")
async def search(query: str = Query(..., description="Search query")):
    """
    Endpoint to perform similarity search in the vector store.
    Returns only the content of the documents.
    """
    found_docs = qdrant_langchain.similarity_search(query, k=5)
    
    return {
        "query": query,
        "results": [doc.page_content for doc in found_docs]
    }

@router.get("/search-detailed")
async def search_detailed(query: str = Query(..., description="Search query")):
    """
    Endpoint to perform similarity search in the vector store.
    Returns content with full metadata for debugging purposes.
    """
    found_docs = qdrant_langchain.similarity_search(query, k=5)
    
    return {
        "query": query,
        "total_results": len(found_docs),
        "results": [
            {
                "content": doc.page_content,
                "metadata": {
                    "source": doc.metadata.get("source", "N/A"),
                    "page": doc.metadata.get("page", "N/A"),
                    "page_label": doc.metadata.get("page_label", "N/A"),
                    "category": doc.metadata.get("category", "N/A"),
                    "total_pages": doc.metadata.get("total_pages", "N/A"),
                    "processed_date": doc.metadata.get("processed_date", "N/A"),
                    "_id": doc.metadata.get("_id", "N/A"),
                }
            }
            for doc in found_docs
        ]
    }