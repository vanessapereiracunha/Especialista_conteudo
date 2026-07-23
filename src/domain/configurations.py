from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class BookConfig(BaseModel):
    title: str
    author: str
    publication_label: str
    source_path: str
    source_format: str
    source_notes: str


class EditorialSettings(BaseModel):
    target_audience: str
    promised_transformation: str
    tone_of_voice: str
    editorial_rules: list[str] = Field(default_factory=list)


class GenerationSettings(BaseModel):
    microbook_min_words: int = 800
    microbook_max_words: int = 1000
    max_source_chars: int = 45000


class LLMSettings(BaseModel):
    provider: str = "openai_compatible"
    temperature: float = 0.3
    review_temperature: float = 0.1


class OutputSettings(BaseModel):
    ideas_map_file: str
    editorial_file: str
    distribution_file: str
    review_file: str
    operations_file: str
    ai_usage_file: str


class AppConfig(BaseModel):
    book: BookConfig
    editorial: EditorialSettings
    generation: GenerationSettings
    llm: LLMSettings
    output: OutputSettings


def load_config(config_path: str | Path) -> AppConfig:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    return AppConfig.model_validate(data)
