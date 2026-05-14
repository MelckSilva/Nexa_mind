"""
Extratores de texto pros tipos de arquivo aceitos pelo NexaMind.
Tipos suportados: pdf, docx, txt, md
"""

from pathlib import Path
from pypdf import PdfReader
import docx


def _extract_pdf(path: Path) -> str:
    """Extrai texto de um PDF (padrão A3 do prof: PdfReader + extract_text)."""
    reader = PdfReader(str(path))
    partes: list[str] = []
    for page in reader.pages:
        texto_pagina = page.extract_text() or ""
        partes.append(texto_pagina)
    return "\n\n".join(partes)


def _extract_docx(path: Path) -> str:
    """Extrai texto de um .docx concatenando parágrafos."""
    documento = docx.Document(str(path))
    return "\n\n".join(p.text for p in documento.paragraphs if p.text.strip())


def _extract_txt(path: Path) -> str:
    """Lê arquivo texto plano (txt ou md). UTF-8."""
    return path.read_text(encoding="utf-8")


# Mapa tipo -> função extratora
_EXTRACTORS = {
    "pdf": _extract_pdf,
    "docx": _extract_docx,
    "txt": _extract_txt,
    "md": _extract_txt,
}


def extract_text(caminho_arquivo: str, tipo_arquivo: str) -> str:
    """
    Extrai texto bruto de um arquivo conforme seu tipo.

    Raises:
        FileNotFoundError: se o arquivo não existir.
        NotImplementedError: se o tipo não tiver extrator implementado.
    """
    path = Path(caminho_arquivo)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    extractor = _EXTRACTORS.get(tipo_arquivo.lower())
    if extractor is None:
        raise NotImplementedError(
            f"Extrator para tipo '{tipo_arquivo}' não implementado. "
            f"Suportados: {list(_EXTRACTORS.keys())}"
        )

    return extractor(path)