from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from domain.configurations import load_config
from domain.models import EditorialKnowledgeMap


def test_config_contains_idea_map_output() -> None:
    config = load_config(PROJECT_ROOT / "config" / "editorial.yaml")
    assert config.output.ideas_map_file == "output/editorial_ideas.json"


def test_editorial_ideas_output_has_required_structure() -> None:
    data = json.loads((PROJECT_ROOT / "output" / "editorial_ideas.json").read_text(encoding="utf-8"))
    idea_map = EditorialKnowledgeMap.model_validate(data)

    assert idea_map.book_title == "A Arte da Guerra"
    assert 5 <= len(idea_map.ideas) <= 8
    assert all(idea.idea_id for idea in idea_map.ideas)
    assert all(idea.source_reference.page_start >= 1 for idea in idea_map.ideas)
