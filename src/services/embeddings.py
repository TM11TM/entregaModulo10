# from google import genai 
from langchain_huggingface import HuggingFaceEmbeddings

embeddings_model_langchain = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")