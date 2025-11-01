import sys; sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()
import asyncio
import json 
import os
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from src.services.llms import llm_langchain
from tenacity import retry, wait_fixed



prompt_template = """
Eres un asistente experto en la creación de resúmenes extremadamente buenos y muy cortos de documentos PDF. 
Tu objetivo es extraer la información clave pero general y presentarla de manera concisa y facil de entender. 
Piensa en que estos resumenes pueden servirte para entender el contenido de un documento sin leerlo. Además 
dale un tema formal y profesional al resumen ya que se trataran de documentos oficiales.

Resume el siguiente documento:

{document_text}

Resumen:
"""

prompt = PromptTemplate(template=prompt_template, input_variables=['document_text'])

# Cadena de resumen utilizando LangChain LLM ye l prompt definido
summarization_chain = prompt | llm_langchain

# Función para resumir un documento PDF
@retry(wait=wait_fixed(2))
async def summarize_document(file_path):
    # Carga
    loader = PyPDFLoader(file_path)
    document = await asyncio.to_thread(loader.load)
    # Concatenar el texto de todas las páginas del documento
    document_text = "\n\n".join(page.page_content for page in document)
    summary = await summarization_chain.ainvoke({"document_text": document_text})
    return summary.content

# Para que el free tier de Google GenAI no de errores por exceso de peticiones
def batched(iterable, n=5):
    # Generador para dividir un iterable en lotes de tamaño n
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]
        
# Programa principal para resumir todos los documentos en la carpeta 'data/optimized_chunks'
async def main():

    to_parse_documnents = os.listdir('data/optimized_chunks')

    # Filtramos solo archivos PDF
    pdf_files = [doc for doc in to_parse_documnents if doc.endswith(".pdf")]

    results = {}

    # Procesamos en lotes de 5 documentos para controlar la cuota
    for batch in batched(pdf_files, 5):
        tasks = []
        for doc_name in batch:
            file_path = os.path.join('data/optimized_chunks', doc_name)
            tasks.append(asyncio.create_task(summarize_document(file_path)))

        # Ejecutamos tareas concurrentemente para el lote actual
        summaries = await asyncio.gather(*tasks)

        # Guardamos los resultados con los nombres de archivo sin extensión
        for doc_name, summary in zip(batch, summaries):
            if summary:
                results[doc_name.replace(".pdf", "")] = summary

        # Pausa para respetar límites de cuota de la API y evitar errores 429
        await asyncio.sleep(30)

    # Guardamos todos los resúmenes juntos en un archivo JSON
    with open('data/summaries.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    

if __name__ == '__main__':
    asyncio.run(main())