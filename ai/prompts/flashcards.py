"""
Prompt template pra geração de flashcards.

A saída precisa ser JSON parseável porque os flashcards vão direto pro
banco via service `criar_flashcard()` do backend. Forçamos a estrutura
no prompt e fazemos parsing tolerante no pipeline.
"""

SYSTEM_PROMPT_FLASHCARDS = """\
Você é um assistente acadêmico especializado em criar flashcards de estudo \
para estudantes universitários. Flashcards bem feitos são objetivos, \
testam um conceito por vez e têm respostas curtas o suficiente pra serem \
memorizadas.

Regras:
- Use APENAS as informações presentes no material fornecido.
- Cada flashcard testa UM conceito ou fato específico (não misture).
- Pergunta clara, sem ambiguidade.
- Resposta direta: idealmente 1-3 frases.
- Classifique cada flashcard em dificuldade: "facil", "medio" ou "dificil".
  * facil: definição direta, fato isolado
  * medio: relação entre conceitos, aplicação simples
  * dificil: raciocínio, comparação, caso de uso complexo
- NÃO invente conteúdo que não esteja no material.
- Idioma: português do Brasil (pt-BR).
- IMPORTANTE: sua resposta deve ser EXCLUSIVAMENTE um JSON válido, sem \
nenhum texto antes ou depois, sem markdown, sem ```json.\
"""


def montar_prompt_flashcards(
    titulo: str, conteudo: str, quantidade: int = 10
) -> list[dict]:
    """
    Monta as mensagens pra gerar `quantidade` flashcards a partir de um material.

    Resposta esperada do LLM (JSON):
        {
          "flashcards": [
            {"pergunta": "...", "resposta": "...", "nivel_dificuldade": "medio"},
            ...
          ]
        }
    """
    user_message = f"""\
Material: "{titulo}"

Conteúdo:
\"\"\"
{conteudo}
\"\"\"

Gere exatamente {quantidade} flashcards a partir deste material.

Retorne APENAS um JSON no formato:
{{
  "flashcards": [
    {{"pergunta": "...", "resposta": "...", "nivel_dificuldade": "facil|medio|dificil"}},
    ...
  ]
}}

Sem texto extra, sem markdown, sem ```json.
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT_FLASHCARDS},
        {"role": "user", "content": user_message},
    ]