"""
Pipeline: chat com RAG + memoria.

Combina as tres aulas do prof:
    A3 (estrutura RAG): embedding da pergunta -> busca por similaridade ->
                        prompt aumentado com o contexto recuperado
    A4 (ChromaDB):      vector store persistente com filtro por metadata
    A5 (Memoria):       historico de mensagens da sessao injetado no prompt

Ponto de entrada principal: `responder_pergunta()`.
"""

from ..core.llm import chat_complete
from ..core.config import RAG_TOP_K
from ..vectorstore.chroma_store import search
from ..prompts.chat import SYSTEM_PROMPT_CHAT, montar_mensagem_usuario


def indexar_material_pipeline(
    material_id: str,
    disciplina_id: str,
    titulo: str,
    caminho_arquivo: str,
    tipo_arquivo: str,
) -> int:
    """
    Pipeline de indexacao chamado apos o upload de um material:
        extrai texto -> chunka -> embeds + upsert no Chroma.

    Returns: numero de chunks indexados.
    """
    from ..ingest.extractors import extract_text
    from ..ingest.chunker import split_text
    from ..vectorstore.chroma_store import index_material

    texto = extract_text(caminho_arquivo, tipo_arquivo)
    chunks = split_text(texto)
    return index_material(
        material_id=material_id,
        disciplina_id=disciplina_id,
        titulo=titulo,
        chunks=chunks,
    )


def responder_pergunta(
    pergunta: str,
    *,
    historico: list[dict] | None = None,
    disciplina_id: str | None = None,
    material_id: str | None = None,
    top_k: int | None = None,
) -> dict:
    """
    Responde uma pergunta usando RAG sobre os materiais indexados.

    Args:
        pergunta: Texto da pergunta atual do aluno.
        historico: Lista [{"role": "user|assistant", "content": "..."}] com as
                   mensagens anteriores da sessao (padrao A5).
        disciplina_id: Restringe a busca aos materiais da disciplina.
        material_id: Restringe a busca a um unico material (precedencia sobre disciplina).
        top_k: Quantos chunks recuperar (default: RAG_TOP_K do .env).

    Returns:
        dict com:
            - resposta: texto gerado pelo LLM (string)
            - fontes: lista de {titulo, material_id, distancia} dos chunks usados
    """
    historico = historico or []
    top_k = top_k if top_k is not None else RAG_TOP_K

    # 1. Recupera chunks relevantes (A3 + A4)
    chunks = search(
        pergunta,
        top_k=top_k,
        disciplina_id=disciplina_id,
        material_id=material_id,
    )

    # 2. Monta mensagens: system + historico + user atual com contexto (A5 + A3)
    user_msg = montar_mensagem_usuario(pergunta, chunks)
    mensagens = (
        [{"role": "system", "content": SYSTEM_PROMPT_CHAT}]
        + historico
        + [{"role": "user", "content": user_msg}]
    )

    # 3. Chama o Groq
    # Temperature aumentada de 0.3 para 0.6 para permitir respostas mais abrangentes
    # e criativas, além de complementar o contexto com conhecimento geral
    resposta_texto = chat_complete(mensagens, temperature=0.6).strip()

    # 4. Monta as fontes (chunks unicos por material)
    fontes_vistas: set[str] = set()
    fontes: list[dict] = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        material_id_chunk = meta.get("material_id")
        if material_id_chunk and material_id_chunk not in fontes_vistas:
            fontes.append(
                {
                    "material_id": material_id_chunk,
                    "titulo": meta.get("titulo", "Material"),
                    "distancia": chunk.get("distancia"),
                }
            )
            fontes_vistas.add(material_id_chunk)

    return {"resposta": resposta_texto, "fontes": fontes}