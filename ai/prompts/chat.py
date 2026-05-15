"""
Prompt pro chat com RAG.

Reutiliza a estrutura do Exemplo 1 da A3 do prof:
    - regras explicitas
    - idioma pt-BR
    - "responda apenas com base no contexto"
Adaptado pra chat com historico e multiplos chunks de contexto.

Montagem em duas partes:
    1. system_prompt: identidade e regras do tutor.
    2. user message: pergunta atual + contexto recuperado.
O historico de mensagens (memoria, padrao A5) e injetado entre as duas.
"""

SYSTEM_PROMPT_CHAT = """\
Voce e o assistente de estudos do NexaMind. Seu papel e ajudar estudantes \
universitarios a entender o conteudo dos materiais que eles enviaram para \
a plataforma.

Regras:
- Responda APENAS com base nos trechos de contexto fornecidos a cada pergunta.
- Nao use conhecimento externo, mesmo que voce saiba a resposta.
- Se a resposta nao estiver claramente no contexto, diga: "Nao encontrei \
essa informacao nos materiais da disciplina."
- Quando citar algo, indique de qual material veio (use o titulo informado \
nos metadados do contexto).
- Seja claro e didatico, mas objetivo. Evite enrolacao.
- NAO mostre seu raciocinio interno; retorne apenas a resposta final.
- Idioma: portugues do Brasil (pt-BR).\
"""


def formatar_contexto(chunks: list[dict]) -> str:
    """
    Formata os chunks recuperados num bloco de contexto legivel para o LLM.

    Cada chunk vem como:
        [Trecho N - "Titulo do Material"]
        <texto do chunk>
    """
    if not chunks:
        return "(nenhum material disponivel como contexto)"

    partes: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        titulo = chunk.get("metadata", {}).get("titulo", "Material")
        texto = chunk.get("texto", "").strip()
        partes.append(f'[Trecho {i} - "{titulo}"]\n{texto}')
    return "\n\n---\n\n".join(partes)


def montar_mensagem_usuario(pergunta: str, chunks: list[dict]) -> str:
    """Mensagem 'user' atual: pergunta enriquecida com o contexto recuperado."""
    contexto = formatar_contexto(chunks)
    return f"""\
Contexto recuperado dos materiais:
\"\"\"
{contexto}
\"\"\"

Pergunta do aluno:
{pergunta}

Resposta:"""