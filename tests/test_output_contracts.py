from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_distribution_output_contains_three_complete_scripts() -> None:
    text = (PROJECT_ROOT / "output" / "distribution.md").read_text(encoding="utf-8")

    assert "## Roteiro 1" in text
    assert "## Roteiro 2" in text
    assert "## Roteiro 3" in text
    assert text.count("**Gancho inicial:**") == 3
    assert text.count("**Desenvolvimento:**") == 3
    assert text.count("**Indicação visual / cena:**") == 3
    assert text.count("**CTA:**") == 3
    assert text.count("**Plataforma prioritária:**") == 3
    assert text.count("**Justificativa da plataforma:**") == 3


def test_review_output_contains_review_decisions() -> None:
    text = (PROJECT_ROOT / "output" / "review.md").read_text(encoding="utf-8")

    assert "## Evidências explícitas da fonte" in text
    assert "## Rastreabilidade da revisão" in text
    assert "**Classificação:**" in text
    assert "## Exemplo mantido" in text
    assert "## Exemplo modificado" in text
    assert "## Exemplo rejeitado" in text


def test_editorial_output_microbook_stays_in_requested_range() -> None:
    text = (PROJECT_ROOT / "output" / "editorial.md").read_text(encoding="utf-8")
    marker = "## Microbook"
    microbook = text.split(marker, 1)[1] if marker in text else text
    word_count = len(re.findall(r"\b\w+\b", microbook, flags=re.UNICODE))

    assert 800 <= word_count <= 1000
