from __future__ import annotations

from application.validators import extract_json_payload
from domain.configurations import AppConfig
from domain.models import EditorialKnowledgeMap, SourceDocument
from infrastructure.llm_client import LLMClient
from pydantic import ValidationError
from prompts.prompts import IDEA_MAP_SYSTEM_PROMPT, build_idea_map_prompt


class IdeaMapperAgent:
    def __init__(self, llm_client: LLMClient, config: AppConfig) -> None:
        self.llm_client = llm_client
        self.config = config

    def run(self, source: SourceDocument) -> EditorialKnowledgeMap:
        guidance = ""

        for attempt in range(3):
            response = self.llm_client.generate(
                system_prompt=IDEA_MAP_SYSTEM_PROMPT,
                user_prompt=build_idea_map_prompt(self.config, source, guidance),
                temperature=self.config.llm.review_temperature,
            )
            payload = extract_json_payload(response)

            try:
                idea_map = EditorialKnowledgeMap.model_validate(payload)
            except ValidationError:
                if attempt == 2:
                    raise
                guidance = (
                    "Retorne novamente com JSON válido contendo book_title e entre 5 e 8 ideias, cada uma com "
                    "idea_id, title, summary, source_reference, themes e evidence_excerpt."
                )
                continue

            evidence_issues: list[str] = []
            factors = ["doutrina", "tempo", "terreno", "mando", "disciplina"]
            for idea in idea_map.ideas:
                excerpt = (idea.evidence_excerpt or "").lower()
                if len(excerpt.strip()) < 80:
                    evidence_issues.append(
                        f"{idea.idea_id}: evidence_excerpt curto demais; inclua um trecho maior do texto para sustentar a ideia."
                    )
                if "cinco" in (idea.summary or "").lower() and "fator" in (idea.summary or "").lower():
                    if sum(1 for term in factors if term in excerpt) < 2:
                        evidence_issues.append(
                            f"{idea.idea_id}: se a ideia envolve os cinco fatores, inclua no evidence_excerpt a enumeração completa se ela aparecer no texto."
                        )

            if evidence_issues and attempt < 2:
                guidance = "Ajuste evidence_excerpt para sustentar melhor cada ideia:\n- " + "\n- ".join(evidence_issues)
                continue

            return idea_map

        raise ValueError("Falha inesperada ao gerar o mapa estruturado de ideias.")
