"""
Pipeline: gera flashcards a partir de um material.

Fluxo:
    1. Extrai texto do arquivo.
    2. Chama o Groq pedindo flashcards em formato JSON.
    3. Faz parsing tolerante (caso o modelo adicione texto extra).
    4. Valida cada flashcard e retorna lista de dicts prontos para
       o backend persistir.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ..core.llm import chat_complete
from ..ingest.extractors import extract_text
from ..ingest.chunker import split_text
from ..prompts.flashcards import montar_prompt_flashcards

# Valores aceitos pelo enum dificuldade_enum do backend
NIVEIS_VALIDOS = {"facil", "medio", "dificil"}


def _extrair_json(resposta: str) -> dict:
    """
    Faz parsing tolerante do JSON retornado pelo LLM.

    Mesmo pedindo "so JSON sem markdown", modelos as vezes incluem
    cercas de markdown ou texto antes/depois. Procuramos o primeiro {
    e o ultimo } e tentamos parsear o que esta entre eles.
    """
    resposta = resposta.strip()

    # Remove cercas de markdown se existirem
    if resposta.startswith("```"):
        resposta = re.sub(r"^```(json)?\s*", "", resposta)
        resposta = re.sub(r"\s*```$", "", resposta)

    # Recorta a partir do primeiro { ate o ultimo }
    inicio = resposta.find("{")
    fim = resposta.rfind("}")
    if inicio == -1 or fim == -1:
        raise ValueError("Resposta do LLM nao contem JSON valido.")

    return json.loads(resposta[inicio : fim + 1])


def _validar_flashcard(card: Any) -> dict | None:
    """Filtra flashcards mal-formados. Retorna o dict normalizado ou None."""
    if not isinstance(card, dict):
        return None
    pergunta = (card.get("pergunta") or "").strip()
    resposta = (card.get("resposta") or "").strip()
    nivel = (card.get("nivel_dificuldade") or "medio").strip().lower()

    if not pergunta or not resposta:
        return None
    if nivel not in NIVEIS_VALIDOS:
        nivel = "medio"

    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "nivel_dificuldade": nivel,
    }


def gerar_flashcards_de_arquivo(
    caminho_arquivo: str,
    tipo_arquivo: str,
    titulo: str,
    quantidade: int = 10,
) -> list[dict]:
    """
    Gera flashcards a partir de um material.

    Pra materiais muito grandes, faz a geracao em lotes (cada lote a partir
    de um chunk grande) e concatena. Evita estourar o contexto do modelo.

    Args:
        caminho_arquivo: Caminho do arquivo.
        tipo_arquivo: pdf, docx, txt, md.
        titulo: Titulo do material.
        quantidade: Total aproximado de flashcards desejados.

    Returns:
        Lista de dicts {pergunta, resposta, nivel_dificuldade} pronta pro backend.
    """
    texto = extract_text(caminho_arquivo, tipo_arquivo).strip()
    if not texto:
        return []

    LIMITE_LOTE_UNICO = 12_000

    if len(texto) <= LIMITE_LOTE_UNICO:
        # Geracao em uma unica chamada
        mensagens = montar_prompt_flashcards(titulo, texto, quantidade)
        resposta = chat_complete(mensagens, temperature=0.4)
        try:
            data = _extrair_json(resposta)
        except (ValueError, json.JSONDecodeError):
            return []
        cards_brutos = data.get("flashcards", [])
        return [c for c in (_validar_flashcard(x) for x in cards_brutos) if c]

    # Material grande: divide em lotes e gera proporcionalmente
    partes = split_text(texto, chunk_size=4000, chunk_overlap=200)
    qtd_por_parte = max(2, quantidade // len(partes))

    todos: list[dict] = []
    for i, parte in enumerate(partes, start=1):
        mensagens = montar_prompt_flashcards(
            f"{titulo} (parte {i}/{len(partes)})", parte, qtd_por_parte
        )
        try:
            resposta = chat_complete(mensagens, temperature=0.4)
            data = _extrair_json(resposta)
            cards = [
                c
                for c in (_validar_flashcard(x) for x in data.get("flashcards", []))
                if c
            ]
            todos.extend(cards)
        except (ValueError, json.JSONDecodeError):
            # Lote falhou: ignora e segue (nao derruba o processo todo)
            continue

    return todos[:quantidade]