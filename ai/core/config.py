"""
Configurações centralizadas da camada de IA.

Lê variáveis do .env (uma vez só, no import) e expõe constantes
que serão usadas pelos demais módulos. Centralizar aqui evita
ter `os.getenv` espalhado pelo código.
"""

import os
from dotenv import load_dotenv

# Carrega o .env que está em ai/ (a pasta acima desta).
# __file__ é o caminho deste config.py.
# os.path.dirname(__file__) é a pasta core/.
# .. sobe uma pasta, chegando em ai/.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


# === Groq ===
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# === Embeddings (A3, A4) ===
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# === ChromaDB ===
# Caminho absoluto pro Chroma persistir os dados.
# Resolvido a partir da raiz do projeto pra funcionar de qualquer lugar.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHROMA_PATH: str = os.path.abspath(
    os.path.join(_PROJECT_ROOT, os.getenv("CHROMA_PATH", "ai/data/chroma"))
)

# === Chunking (vamos usar na Fase 3) ===
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

# === RAG (vamos usar na Fase 4) ===
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "4"))


def validate() -> None:
    """Verifica se as variáveis críticas estão configuradas."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY não está configurada. "
            "Defina no arquivo ai/.env."
        )