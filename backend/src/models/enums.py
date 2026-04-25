from sqlalchemy.dialects.postgresql import ENUM

tipo_arquivo_enum = ENUM(
    "pdf", "pptx", "docx", "txt", "md", "outro",
    name="tipo_arquivo_enum",
    create_type=False
)

dificuldade_enum = ENUM(
    "facil", "medio", "dificil",
    name="dificuldade_enum",
    create_type=False
)

papel_mensagem_enum = ENUM(
    "usuario", "assistente",
    name="papel_mensagem_enum",
    create_type=False
)