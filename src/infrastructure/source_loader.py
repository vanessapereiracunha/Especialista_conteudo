from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from domain.models import SourceDocument, SourcePage


class SourceLoader:
    def load(self, source_path: str | Path) -> SourceDocument:
        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo-fonte não encontrado em {path}. Coloque o material em data/source/ e atualize config/editorial.yaml se necessário."
            )

        if path.suffix.lower() == ".pdf":
            return self._load_pdf(path)
        if path.suffix.lower() == ".txt":
            return self._load_txt(path)

        raise ValueError(f"Formato de fonte não suportado: {path.suffix}")

    def _load_pdf(self, path: Path) -> SourceDocument:
        reader = PdfReader(str(path))
        pages: list[SourcePage] = []

        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            pages.append(SourcePage(page_number=index, text=text))

        full_text = "\n\n".join(page.text for page in pages if page.text)
        if not full_text.strip():
            raise ValueError("O PDF foi carregado, mas nenhum texto extraível foi encontrado.")

        return SourceDocument(source_path=str(path), pages=pages, full_text=full_text)

    def _load_txt(self, path: Path) -> SourceDocument:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError("O arquivo TXT está vazio.")

        return SourceDocument(
            source_path=str(path),
            pages=[SourcePage(page_number=1, text=text)],
            full_text=text,
        )
