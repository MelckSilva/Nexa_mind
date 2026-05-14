"""
Pipeline: gera resumo de um material acadêmico.

Fluxo:
    1. Extrai texto do arquivo (PDF, DOCX, TXT, MD)
    2. Se for muito grande, faz um pré-resumo (map-reduce simples)
    3. Chama o Groq com o prompt de resumo
    4. Retorna o texto markdown final

Função principal: `gerar_resumo_de_arquivo` — é o que o backend vai chamar.
"""

from ..core.llm import chat_complete
from ..ingest.extractors import extract_text
from ..ingest.chunker import split_text
from ..prompts.resumo import montar_prompt_resumo

# Materiais maiores que este limite (em chars) usam estratégia map-reduce:
# resumir cada parte e depois consolidar. Abaixo disso, mandamos o texto inteiro.
LIMITE_TEXTO_INTEIRO = 12_000


def _resumir_texto(titulo: str, conteudo: str) -> str:
    """Chama o Groq uma única vez para resumir o conteúdo."""
    mensagens = montar_prompt_resumo(titulo, conteudo)
    return chat_complete(mensagens, temperature=0.3).strip()


def _resumir_em_map_reduce(titulo: str, texto: str) -> str:
    """
    Estratégia map-reduce para textos grandes:
        1. (map) Resume cada chunk grande individualmente.
        2. (reduce) Junta os mini-resumos e gera o resumo final.

    Isso evita estourar o contexto do modelo em PDFs longos.
    """
    # Chunks bem maiores que os do RAG (4000 chars) porque resumir
    # pedaços pequenos demais perde o fio da meada.
    partes = split_text(texto, chunk_size=4000, chunk_overlap=200)

    # Map: resume cada parte
    mini_resumos: list[str] = []
    for i, parte in enumerate(partes, start=1):
        mini = _resumir_texto(f"{titulo} (parte {i}/{len(partes)})", parte)
        mini_resumos.append(mini)

    # Reduce: junta os mini-resumos num único resumo final
    consolidado = "\n\n".join(mini_resumos)
    return _resumir_texto(titulo, consolidado)


def gerar_resumo_de_arquivo(
    caminho_arquivo: str,
    tipo_arquivo: str,
    titulo: str,
) -> str:
    """
    Gera o resumo de um material acadêmico.

    Args:
        caminho_arquivo: Caminho do arquivo no disco.
        tipo_arquivo: pdf, docx, txt, md.
        titulo: Título legível do material (vai no prompt).

    Returns:
        Resumo em markdown.

    Raises:
        FileNotFoundError, NotImplementedError, RuntimeError (Groq).
    """
    texto = extract_text(caminho_arquivo, tipo_arquivo).strip()

    if not texto:
        return "_Não foi possível extrair texto deste material._"

    if len(texto) <= LIMITE_TEXTO_INTEIRO:
        return _resumir_texto(titulo, texto)

    return _resumir_em_map_reduce(titulo, texto)