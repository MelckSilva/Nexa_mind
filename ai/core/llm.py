"""
Cliente Groq centralizado.

Mantém um único cliente reutilizável por toda a camada de IA,
evitando recriar a conexão a cada chamada.

Padrão das aulas A3 e A5 do prof, mas encapsulado numa função
chat_complete() que simplifica o uso nos pipelines.
"""

from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL

# Inicialização lazy: só cria o cliente quando alguém chamar get_client().
# Isso evita falhar no import caso GROQ_API_KEY esteja vazia.
_client: Groq | None = None


def get_client() -> Groq:
    """Retorna o cliente Groq compartilhado."""
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY não definida. Cheque o .env.")
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def chat_complete(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float = 0.3,
) -> str:
    """
    Chama o endpoint chat.completions do Groq e retorna apenas o texto.

    Args:
        messages: Lista no formato [{"role": "...", "content": "..."}].
        model: Override do modelo (default: GROQ_MODEL do .env).
        temperature: Criatividade (0 = determinístico, 1 = muito criativo).
                     Padrão 0.3 = respostas factuais (bom pra resumo/RAG).
    """
    client = get_client()
    response = client.chat.completions.create(
        model=model or GROQ_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""