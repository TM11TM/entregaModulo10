# 📚 Sistema RAG para Consulta del BOE

Sistema de Retrieval-Augmented Generation (RAG) para consultar el Boletín Oficial del Estado español utilizando búsqueda vectorial semántica y modelos de lenguaje.

## 🎯 Características

- **Búsqueda semántica avanzada** usando embeddings de Gemini
- **Base de datos vectorial** con Qdrant (índice HNSW optimizado)
- **Generación de respuestas** con Gemini 2.5 Flash Lite
- **Selección inteligente de fuentes** basada en categorías del BOE
- **API REST** construida con FastAPI
- **Actualización incremental** de documentos sin reindexación completa
- **Filtrado por metadata** (categoría, fecha, artículo, sección)

## 🏗️ Arquitectura

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ HTTP Request
       ▼
┌──────────────────────────────┐
│   FastAPI Router             │
│  /langchain/rag              │
│  /langchain/search           │
│  /langchain/detailed-search  │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│        RAG Chain Pipeline           │
│  1. Source Selection (Gemini LLM)   │
│  2. Query Embedding (Gemini)        │
│  3. Vector Search (Qdrant)          │
│  4. Context Optimization            │
│  5. Response Generation (Gemini)    │
└──────┬─────────┬──────────┬─────────┘
       │         │          │
       ▼         ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Gemini │ │ BAAI/  │ │ Qdrant │
   │  LLM   │ │ bge-m3 │ │ Vector │
   │        │ │   HF   │ │   DB   │
   └────────┘ └────────┘ └────────┘
```

## 📋 Requisitos

- Python 3.12+
- Qdrant (local o cloud)
- Google API Key (para Gemini)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd entregaModulo10
```

### 2. Crear entorno virtual

Crearemos el entorno virtual con UV y el project.toml
```bash
uv sync 
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Google AI API
GOOGLE_API_KEY=tu_api_key_aquí
```

### 5. Iniciar Qdrant (Docker)

```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

O con docker-compose:

```yaml
# docker-compose.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

```bash
docker-compose up -d
```

## 📂 Estructura del Proyecto

```
entregaModulo10/
├── qdrant_config/
│   ├── config.yaml               # Configuracion QDrant
├── qdrant_data/
│
├── data/
│   ├── optimized_chunks/         # PDFs procesados 
│   ├── pdfs/                     # PDFs enteros
│   └── summaries.json            # Resúmenes de categorías
│
├── scripts/
│   ├── langchain_index .py       # Indice de langchain con BGE
│   ├── routing_generation.py     # Generacion de resumenes concisos
│   └── preprocessing.py          # Script de carga inicial
│ 
├── src/
│   ├── api/
│   │   ├── router_langchain.py   # Endpoints FastAPI
│   │   └── schema.py             # Modelos Pydantic
│   ├── process_langchain/
│   │   ├── __init__.py           # Exports y summaries
│   │   ├── chain.py              # Pipeline RAG
│   │   ├── prompts.py            # Prompts del sistema
│   │   └── structures.py         # Modelos de datos
│   ├── services/
│   │   ├── embeddings.py         # Configuración embeddings
│   │   ├── llms.py               # Configuración LLMs
│   │   └── vector_store.py       # Cliente Qdrant
│   ├── app.py                    # FastAPI app
│   └── main.py                   # Entry point
├── .env                          # Variables de entorno
├── docker-compose.yaml           # Contenedores Docker
├── pyproject.toml                # Sincronizar dependecias
└── README.md
```

## 🔧 Configuración Inicial

### 1. Preparar datos

Coloca tus PDFs del BOE en `data/pdfs/`:

### 2. uv run (summaries.json)

Crea `data/summaries.json`:

```json
[
  {
    "title": "Sección 1.ª De los derechos fundamentales",
    "summary": "Contiene los derechos fundamentales de la Constitución Española..."
  },
  {
    "title": "Sección 2.ª De los derechos y deberes",
    "summary": "Detalla los derechos y deberes de los ciudadanos españoles..."
  }
]
```

### 3. Cargar documentos en Qdrant

```bash
python scripts/preprocessing.py
```

Esto procesará todos los PDFs y los cargará en la base de datos vectorial.

### 4. Iniciar la aplicación

```bash
python src/main.py
```

La API estará disponible en: `http://localhost:8000`

## 📖 Uso de la API

### Documentación Interactiva

Accede a la documentación automática en:

```
http://localhost:8000/docs
```

### Endpoints Disponibles

#### 1. **Consulta RAG** (Principal)

**POST** `/langchain/rag`

Realiza una consulta completa con selección de fuente, búsqueda vectorial y generación de respuesta.

```bash
curl -X POST "http://localhost:8000/langchain/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué dice la Constitución sobre el derecho a la educación?"
  }'
```

**Respuesta:**
```json
{
  "question": "¿Qué dice la Constitución sobre el derecho a la educación?",
  "answer": "Según el Artículo 27 de la Constitución Española...",
  "source": "Sección 1.ª De los derechos fundamentales",
  "source_reason": "La pregunta se refiere a derechos fundamentales..."
}
```

#### 2. **Búsqueda Semántica Simple**

**GET** `/langchain/search?query={tu_consulta}`

Devuelve solo el contenido de los documentos más relevantes.

```bash
curl "http://localhost:8000/langchain/search?query=educación"
```

**Respuesta:**
```json
{
  "query": "educación",
  "results": [
    "Artículo 27. Todos tienen el derecho a la educación...",
    "Artículo 28. Todos tienen derecho a sindicarse..."
  ]
}
```

#### 3. **Búsqueda con Metadatos**

**GET** `/langchain/search-detailed?query={tu_consulta}`

Devuelve documentos con metadata completa para debugging.

```bash
curl "http://localhost:8000/langchain/search-detailed?query=educación"
```

**Respuesta:**
```json
{
  "query": "educación",
  "total_results": 5,
  "results": [
    {
      "content": "Artículo 27...",
      "metadata": {
        "source": "Sección 1.ª",
        "page": 1,
        "category": "BOE actual",
        "article_number": "27"
      }
    }
  ]
}
```

## 📊 Monitoreo y Logs

### Logs de Uvicorn

``` bash
# Ver logs en tiempo real
tail -f logs/uvicorn.log

# Logs con nivel de detalle
python src/main.py --log-level debug
```

### Estadísticas de Qdrant

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
info = client.get_collection("langchain_index")

print(f"Documentos: {info.points_count}")
print(f"Dimensión: {info.config.params.vectors.size}")
print(f"Índice: {info.config.optimizer_config}")
```

## 🔄 Actualización de Datos

### Actualización manual

```bash
# 1. Añadir nuevos PDFs a data/optimized_chunks/
# 2. Ejecutar script de actualización
python scripts/update_qdrant.py
```

### Actualización incremental

```python
from src.services.vector_store import qdrant_langchain
from langchain.schema import Document

# Añadir documento nuevo
new_doc = Document(
    page_content="Artículo X. Nuevo contenido...",
    metadata={
        "source": "Nueva Ley",
        "category": "BOE actual",
        "article_number": "X"
    }
)

qdrant_langchain.add_documents([new_doc])
```
### Error 429: Rate Limit Exceeded

**Solución:** Aumenta el `time.sleep()` en `langchain_index.py`:

```python
time.sleep(60)  # Esperar 60 segundos entre batches
```

### Qdrant no responde

```bash
# Verificar que está corriendo
docker ps | grep qdrant

# Ver logs
docker logs <container_id>

# Reiniciar
docker restart <container_id>
```

## 🔐 Seguridad

### Variables de entorno

**NUNCA** commitees `.env` al repositorio:

```bash
# .gitignore
.env
.env.local
*.key
```

- Proyecto: Módulo 10 - PONTIA

## 🙏 Agradecimientos

- [LangChain](https://langchain.com/) - Framework RAG
- [Qdrant](https://qdrant.tech/) - Base de datos vectorial
- [Google Gemini](https://deepmind.google/technologies/gemini/) - LLM y Embeddings
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web

## 📚 Referencias

- [Documentación Qdrant](https://qdrant.tech/documentation/)
- [Documentación LangChain](https://python.langchain.com/docs/get_started/introduction)
- [Gemini API Docs](https://ai.google.dev/docs)
- [BOE - Datos Abiertos](https://www.boe.es/datosabiertos/)

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!


