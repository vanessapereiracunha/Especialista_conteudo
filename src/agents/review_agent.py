from __future__ import annotations

from application.validators import extract_json_payload
from domain.configurations import AppConfig
from domain.models import EditorialKnowledgeMap, EditorialOutput, ReviewReport, SourceDocument
from infrastructure.llm_client import LLMClient
from prompts.prompts import REVIEW_SYSTEM_PROMPT, build_review_prompt
from pydantic import ValidationError


class ReviewAgent:
    def __init__(self, llm_client: LLMClient, config: AppConfig) -> None:
        self.llm_client = llm_client
        self.config = config

    def _contains_forbidden_terms(self, review: ReviewReport) -> bool:
        text = " ".join(
            [
                review.verdict,
                review.adherence_summary,
                " ".join(review.strengths),
                " ".join(review.possible_unsupported_claims),
                " ".join(review.must_fix),
                " ".join(review.minor_edits),
                " ".join(item.claim for item in review.traceability_items),
                " ".join(item.observation for item in review.traceability_items),
            ]
        ).lower()
        return "swot" in text

    def _sanitize_review(self, review: ReviewReport, source: SourceDocument, idea_map: EditorialKnowledgeMap) -> ReviewReport:
        def keep(text: str) -> bool:
            return "swot" not in text.lower()

        strengths = [item for item in review.strengths if keep(item)]
        unsupported = [item for item in review.possible_unsupported_claims if keep(item)]
        must_fix = [item for item in review.must_fix if keep(item)]
        minor_edits = [item for item in review.minor_edits if keep(item)]

        traceability_items = []
        for item in review.traceability_items:
            if not keep(item.claim) or not keep(item.observation):
                continue
            if item.claim.strip().lower().startswith("em uma aplicação contempor"):
                continue
            classification = item.classification
            if classification.strip().lower() == "citação direta" and not self._citation_is_plausible(
                item.claim, source, idea_map
            ):
                classification = "Paráfrase fiel"
            observation = item.observation
            if "citação direta" in observation.lower() and classification.strip().lower() != "citação direta":
                observation = observation.replace("citação direta do material-fonte", "paráfrase fiel ao material-fonte")
                observation = observation.replace("Citação direta do material-fonte", "Paráfrase fiel ao material-fonte")
                observation = observation.replace("citação direta", "paráfrase fiel")
                observation = observation.replace("Citação direta", "Paráfrase fiel")
            if not any(word in observation.lower() for word in ["manter", "reformular", "rejeitar"]):
                observation = f"{observation} Ação recomendada: Manter."
            traceability_items.append(item.model_copy(update={"classification": classification, "observation": observation}))

        kept_example = review.kept_example
        kept_reason = kept_example.reason
        if "citação direta" in kept_reason.lower() and not self._citation_is_plausible(kept_example.content, source, idea_map):
            kept_example = kept_example.model_copy(
                update={"reason": "É uma paráfrase fiel ao material-fonte e reflete a essência da ideia."}
            )

        modified_example = review.modified_example
        modified_reason = modified_example.reason
        if "citação direta" in modified_reason.lower() and not self._citation_is_plausible(
            modified_example.content, source, idea_map
        ):
            modified_example = modified_example.model_copy(
                update={"reason": "O trecho deve ser apresentado como paráfrase fiel e, se houver aplicação contemporânea, ela precisa ser explicitamente marcada."}
            )

        rejected_example = review.rejected_example
        if not keep(rejected_example.content) or not keep(rejected_example.reason):
            rejected_example = rejected_example.model_copy(
                update={
                    "content": "A guerra é uma metáfora direta para competição empresarial.",
                    "reason": "A formulação extrapola o material-fonte e transforma uma leitura editorial em afirmação do autor.",
                }
            )

        return review.model_copy(
            update={
                "strengths": strengths,
                "possible_unsupported_claims": unsupported,
                "must_fix": must_fix,
                "minor_edits": minor_edits,
                "traceability_items": traceability_items,
                "kept_example": kept_example,
                "modified_example": modified_example,
                "rejected_example": rejected_example,
            }
        )

    def _citation_is_plausible(self, claim: str, source: SourceDocument, idea_map: EditorialKnowledgeMap) -> bool:
        normalized_claim = claim.strip()
        if not normalized_claim:
            return False
        if normalized_claim in (source.full_text or ""):
            return True
        return any(normalized_claim in idea.evidence_excerpt for idea in idea_map.ideas)

    def _quality_issues(self, review: ReviewReport, source: SourceDocument, idea_map: EditorialKnowledgeMap) -> list[str]:
        issues: list[str] = []
        if not (3 <= len(review.traceability_items) <= 5):
            issues.append("Traceability deve ter 3 a 5 itens.")
        if self._contains_forbidden_terms(review):
            issues.append("Não inclua frameworks modernos (ex.: SWOT).")

        for item in review.traceability_items:
            if item.claim.strip().lower().startswith("em uma aplicação contempor"):
                issues.append("A afirmação não deve ser uma frase de aplicação contemporânea; use uma afirmação do texto e classifique a ponte na observação.")
                break

            action_ok = any(word in item.observation.lower() for word in ["manter", "reformular", "rejeitar"])
            if not action_ok:
                issues.append("Cada observation deve conter uma ação: Manter | Reformular | Rejeitar.")
                break

            if item.classification.strip().lower() == "citação direta":
                if not self._citation_is_plausible(item.claim, source, idea_map):
                    issues.append("Citação direta só quando a frase existir literalmente na fonte/evidência.")
                    break

        return issues

    def run(
        self,
        source: SourceDocument,
        idea_map: EditorialKnowledgeMap,
        editorial: EditorialOutput,
    ) -> ReviewReport:
        guidance = ""

        for attempt in range(3):
            response = self.llm_client.generate(
                system_prompt=REVIEW_SYSTEM_PROMPT,
                user_prompt=build_review_prompt(
                    self.config,
                    source,
                    idea_map,
                    editorial,
                    extra_guidance=guidance,
                ),
                temperature=self.config.llm.review_temperature,
            )
            payload = extract_json_payload(response)

            try:
                review = ReviewReport.model_validate(payload)
            except ValidationError:
                if attempt == 2:
                    raise
                guidance = (
                    "A resposta anterior veio com estrutura incompleta. Retorne novamente um JSON válido com veredito, "
                    "síntese, listas e 3-5 itens de rastreabilidade com observação específica."
                )
                continue

            issues = self._quality_issues(review, source, idea_map)
            if issues and attempt < 2:
                guidance = (
                    "Ajuste o relatório para ficar mais rigoroso:\n"
                    "- Proibido citar SWOT ou frameworks modernos.\n"
                    "- Use Citação direta somente se a frase estiver literalmente no texto-fonte; caso contrário use Paráfrase fiel.\n"
                    "- Em cada observation, inclua: trecho analisado, problema/acerto e ação recomendada (Manter|Reformular|Rejeitar).\n"
                    f"Problemas detectados: {', '.join(issues)}"
                )
                continue

            sanitized = self._sanitize_review(review, source, idea_map)
            sanitized_issues = self._quality_issues(sanitized, source, idea_map)
            if sanitized_issues and attempt < 2:
                guidance = (
                    "Ajuste o relatório para ficar mais rigoroso:\n"
                    "- Proibido citar SWOT ou frameworks modernos.\n"
                    "- Use Citação direta somente se a frase estiver literalmente no texto-fonte; caso contrário use Paráfrase fiel.\n"
                    "- Em cada observation, inclua: trecho analisado, problema/acerto e ação recomendada (Manter|Reformular|Rejeitar).\n"
                    f"Problemas detectados: {', '.join(sanitized_issues)}"
                )
                continue

            return sanitized

        raise ValueError("Falha inesperada ao gerar revisão editorial válida.")
