from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.content_pipeline import render_operational_response
from application.validators import count_words, ensure_range
from domain.configurations import load_config


def test_load_config_reads_expected_metadata() -> None:
    config = load_config(PROJECT_ROOT / "config" / "editorial.yaml")
    assert config.book.title == "A Arte da Guerra"
    assert config.generation.microbook_min_words == 800


def test_count_words_counts_unicode_words() -> None:
    text = "Estratégia clara vence improviso."
    assert count_words(text) == 4


def test_ensure_range_accepts_valid_value() -> None:
    ensure_range(900, 800, 1000, "Microbook")


def test_render_operational_response_covers_required_topics() -> None:
    content = render_operational_response()
    assert "prioridade" in content.lower()
    assert "paralelo" in content.lower()
    assert "processo" in content.lower()
