from pypdf import PdfReader, PdfWriter
from pypdf.generic import Destination
from typing import Dict, List, Any
from pathlib import Path
import os
import re
import json

# Rutas para los 
BASE_DIR = Path(__file__).resolve().parent.parent 
DATA_DIR = BASE_DIR / "data"
PDFS_DIR = DATA_DIR / "pdfs"  # Carpeta con múltiples PDFs para procesar
OUTPUT_DIR = DATA_DIR / "optimized_chunks"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Recorremos la informacion y recuperamos el titulo, numero de pagina y chunk
def extract_outline_info(reader: PdfReader, outline, level=0):
    info = []
    for item in outline:
        if isinstance(item, list):
            info.extend(extract_outline_info(reader, item, level + 1))
        elif isinstance(item, Destination):
            info.append({
                "title": item.title,
                "page_number": reader.get_destination_page_number(item),
                "chunk_level": level
            })
    return info

# Procesamos los PDFs y los dicidimos en secciones definidas por bookmarks de nivel 1
def process_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    #Load
    reader = PdfReader(str(pdf_path))
    bookmarks = extract_outline_info(reader, reader.outline)

    # Extraer títulos de capítulos (nivel 1)
    chunk_level_info = [item['title'] for item in bookmarks if item['chunk_level'] == 1]

    # Extraer todos bookmarks con info básica
    all_bookmark_info = [{"title": item["title"], "start_page": item["page_number"]} for item in bookmarks]

    # Filtrar solo los bookmarks que sean capítulos (nivel 1)
    filtered_bookmarks = [item for item in all_bookmark_info if item['title'] in chunk_level_info]

    final_pages_division_info = []
    final_page = len(reader.pages)

    # Final de la página de cada sección
    for item, next_item in zip(filtered_bookmarks, filtered_bookmarks[1:] + [None]):
        end_page = next_item['start_page'] - 1 if next_item else final_page - 1
        final_pages_division_info.append({
            **item,
            'final_page': end_page
        })

    # Guardamos las seecciones como PDFs y con los metadatos
    metadata_list = []
    for section in final_pages_division_info:
        writer = PdfWriter()
        name = section['title']
        start_page = section['start_page']
        end_page = section['final_page']

        if end_page >= start_page:
            for page_num in range(start_page, end_page + 1):
                writer.add_page(reader.pages[page_num])

            # Limpiar nombre para archivo
            clean_name = re.sub(r'[\\/*?:"<>|]', "_", name)
            output_path = OUTPUT_DIR / f"{clean_name}.pdf"

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            metadata_list.append({
                "title": name,
                "path": str(output_path),
                "start_page": start_page,
                "end_page": end_page,
                "source_pdf": str(pdf_path)
            })

    return metadata_list

# Procesa PDFs y los guardamos ene l json
def process_multiple_pdfs(pdfs_dir: Path):
    all_metadata = []

    pdf_files = list(pdfs_dir.glob('*.pdf'))
    print(f"Procesando {len(pdf_files)} archivos PDF...")

    for pdf_file in pdf_files:
        print(f"Procesando {pdf_file.name}...")
        metadata = process_pdf(pdf_file)
        all_metadata.extend(metadata)

    # Guardar JSON con información de todos los segmentos
    json_path = DATA_DIR / "summaries.json"  
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump(all_metadata, jf, ensure_ascii=False, indent=4)

    print(f"Procesamiento completo. Metadata guardada en {json_path}")

process_multiple_pdfs(PDFS_DIR)       