from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.source_loader import SourceLoader


def test_source_loader_extracts_pdf_text() -> None:
    loader = SourceLoader()
    source = loader.load(PROJECT_ROOT / "data" / "source" / "a_arte_da_guerra.pdf")
    assert source.pages
    assert "A arte da guerra".lower() in source.full_text.lower()
