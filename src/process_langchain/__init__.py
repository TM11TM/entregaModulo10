# src/process_langchain/__init__.py

import json

# Cargar summaries
with open("data/summaries.json", "r", encoding='utf-8') as f:
    summaries_list = json.load(f)

summaries = {item['title']: item for item in summaries_list}
summaries['none'] = 'Este resumen se utiliza para conversaciones que no tengan que ver con el resto de las tematicas, sean saludos, deseos o cualquier pregunta fuera del contexto del Boletín oficial del estado español'

# Importar los prompts y modelos
from .prompts import source_selection_prompt, rag_prompt, none_selection_prompt
from .structures import SourceModel

# Exportar todo lo necesario
__all__ = [
    'summaries', 
    'source_selection_prompt', 
    'rag_prompt', 
    'none_selection_prompt', 
    'SourceModel'
]