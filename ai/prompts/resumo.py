"""
Prompt template pra geração de resumo de material acadêmico.

Inspirado no prompt do Exemplo 1 da A3 do prof:
    - regras explícitas (responder com base no contexto)
    - idioma fixado em pt-BR
    - "NÃO mostre seu raciocínio interno"

Pra resumos, ajustamos: o objetivo NÃO é responder uma pergunta,
mas sintetizar o material em pontos-chave organizados.
"""

SYSTEM_PROMPT_RESUMO = """\
Você é um assistente acadêmico especialista em criar resumos didáticos para \
estudantes universitários. Seu trabalho é transformar materiais densos em \
sínteses claras e organizadas.

Regras:
- Use APENAS as informações presentes no material fornecido.
- Não invente dados, fórmulas, datas ou nomes que não estejam no texto.
- Seja objetivo: priorize conceitos centrais, definições e exemplos importantes.
- Estruture o resumo com seções claras usando markdown (## para tópicos).
- NÃO mostre seu raciocínio interno; retorne apenas o resumo final.
- Idioma: responda obrigatoriamente em português do Brasil (pt-BR).\
"""


def montar_prompt_resumo(titulo: str, conteudo: str) -> list[dict]:
    """
    Monta a lista de mensagens para gerar um resumo.

    Args:
        titulo: Título do material (vai no prompt pra contextualizar).
        conteudo: Texto extraído do material.
    """
    user_message = f"""\
Material: "{titulo}"

Conteúdo:
\"\"\"
{conteudo}
\"\"\"

Gere um resumo estruturado deste material, com:
1. **Visão geral** (2-3 linhas).
2. **Conceitos principais** (lista com explicações curtas).
3. **Pontos importantes para a prova** (bullets objetivos).

Use markdown. Não inclua nada além do resumo.
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT_RESUMO},
        {"role": "user", "content": user_message},
    ]