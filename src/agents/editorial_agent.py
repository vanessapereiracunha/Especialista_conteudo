from __future__ import annotations

from application.validators import count_words
from application.validators import extract_json_payload
from domain.configurations import AppConfig
from domain.models import EditorialKnowledgeMap, EditorialOutput, SourceDocument
from infrastructure.llm_client import LLMClient
from pydantic import ValidationError
from prompts.prompts import (
    EDITORIAL_EXPANSION_SYSTEM_PROMPT,
    EDITORIAL_SYSTEM_PROMPT,
    build_editorial_expansion_prompt,
    build_editorial_prompt,
)


class EditorialAgent:
    def __init__(self, llm_client: LLMClient, config: AppConfig) -> None:
        self.llm_client = llm_client
        self.config = config

    def _sanitize_microbook_markdown(self, microbook_markdown: str) -> str:
        replacements = [
            ("ambientes competitivos", "cenários de disputa"),
            ("ambiente competitivo", "cenário de disputa"),
            ("ambiente corporativo", "ambiente profissional"),
            ("ambientes corporativos", "ambientes profissionais"),
            ("timing de mercado", "timing do contexto"),
            ("análise de mercado", "análise de contexto"),
            ("se posicionam no mercado", "se posicionam no contexto"),
            ("se posiciona no mercado", "se posiciona no contexto"),
            ("posicionam no mercado", "se posicionam no contexto"),
            ("posiciona no mercado", "se posiciona no contexto"),
            ("vantagem competitiva", "vantagem estratégica"),
            ("ambientes de negócios", "ambientes profissionais"),
            ("ambiente de negócios", "ambiente profissional"),
            ("no contexto de negócios", "no contexto contemporâneo"),
            ("contexto de negócios", "contexto contemporâneo"),
            ("marketing", "comunicação"),
            ("concorrência", "disputa"),
            ("concorrentes", "outros atores"),
            ("concorrente", "outro ator"),
            ("Mercado", "Contexto"),
            ("mercado", "contexto"),
            ("Negócios", "Contextos profissionais"),
            ("negócios", "contextos profissionais"),
        ]

        sanitized = microbook_markdown
        for old, new in replacements:
            sanitized = sanitized.replace(old, new)
        sanitized = sanitized.replace("se se posicionam", "se posicionam")
        return sanitized

    def run(
        self,
        source: SourceDocument,
        idea_map: EditorialKnowledgeMap,
        extra_guidance: str = "",
    ) -> EditorialOutput:
        guidance = extra_guidance

        for attempt in range(5):
            response = self.llm_client.generate(
                system_prompt=EDITORIAL_SYSTEM_PROMPT,
                user_prompt=build_editorial_prompt(self.config, source, idea_map, guidance),
                temperature=self.config.llm.temperature,
            )
            payload = extract_json_payload(response)

            try:
                editorial_output = EditorialOutput.model_validate(payload)
            except ValidationError:
                if attempt == 4:
                    raise
                guidance = (
                    "A resposta anterior veio com estrutura incompleta. Retorne novamente um JSON válido contendo "
                    "briefing completo, microbook_title e microbook_markdown como string não vazia."
                )
                continue

            word_count = count_words(editorial_output.microbook_markdown)
            if word_count < self.config.generation.microbook_min_words and attempt < 4:
                guidance = (
                    f"O microbook anterior veio curto, com {word_count} palavras. "
                    f"Reescreva em JSON válido e entregue entre "
                    f"{self.config.generation.microbook_min_words} e {self.config.generation.microbook_max_words} palavras, "
                    "com introdução, cinco seções desenvolvidas e conclusão."
                )
                continue

            microbook_lower = editorial_output.microbook_markdown.lower()
            if ("metáfora" in microbook_lower and "negóci" in microbook_lower) and attempt < 4:
                guidance = (
                    "Evite tratar guerra como metáfora direta para negócios. Quando fizer aplicação contemporânea, "
                    "marque explicitamente como leitura editorial do presente e mantenha o texto-fonte como referência."
                )
                continue

            modern_terms = ["swot"]
            if any(term in microbook_lower for term in modern_terms) and attempt < 4:
                guidance = (
                    "Remova referências a frameworks modernos (ex.: SWOT). Se fizer ponte contemporânea, use linguagem "
                    "genérica de avaliação de contexto, sem citar ferramentas específicas."
                )
                continue

            contemporary_terms = ["negóci", "mercado", "marketing", "concorr", "empresa", "corporat"]
            has_contemporary = any(term in microbook_lower for term in contemporary_terms)
            has_marker = "leitura contempor" in microbook_lower or "aplicação contempor" in microbook_lower
            if has_contemporary and not has_marker and attempt < 4:
                guidance = (
                    "Quando fizer aplicação para contextos atuais, use marcadores linguísticos claros como "
                    "'Em leitura contemporânea,' ou 'Em uma aplicação contemporânea,' para não confundir com afirmação "
                    "do texto original."
                )
                continue

            forbidden_modernization_terms = [
                "marketing",
                "mercado",
                "concorr",
                "corporat",
                "competit",
                "sobrevivência empresarial",
            ]
            if any(term in microbook_lower for term in forbidden_modernization_terms) and attempt < 4:
                guidance = (
                    "Evite exemplos específicos de marketing/mercado/concorrência e formulações como 'sobrevivência empresarial'. "
                    "Reescreva usando aplicações genéricas (decisões de alto impacto, leitura de contexto, prioridade, recursos e consequências) "
                    "e marque explicitamente quando for aplicação contemporânea."
                )
                continue

            sanitized = self._sanitize_microbook_markdown(editorial_output.microbook_markdown)
            return editorial_output.model_copy(update={"microbook_markdown": sanitized})

        raise ValueError("Falha inesperada ao gerar saída editorial válida.")

    def expand_microbook(
        self,
        source: SourceDocument,
        idea_map: EditorialKnowledgeMap,
        editorial: EditorialOutput,
        current_word_count: int,
    ) -> EditorialOutput:
        guidance = ""

        for attempt in range(5):
            response = self.llm_client.generate(
                system_prompt=EDITORIAL_EXPANSION_SYSTEM_PROMPT,
                user_prompt=build_editorial_expansion_prompt(
                    self.config,
                    source,
                    idea_map,
                    editorial,
                    current_word_count,
                )
                + (f"\n\nOrientação adicional: {guidance}" if guidance else ""),
                temperature=self.config.llm.temperature,
            )
            payload = extract_json_payload(response)

            try:
                expanded = EditorialOutput.model_validate(payload)
            except ValidationError:
                if attempt == 4:
                    raise
                guidance = (
                    "Retorne novamente com briefing completo, microbook_title e microbook_markdown preenchido "
                    "como string não vazia."
                )
                continue

            microbook_lower = expanded.microbook_markdown.lower()
            forbidden_modernization_terms = [
                "marketing",
                "mercado",
                "concorr",
                "corporat",
                "competit",
                "sobrevivência empresarial",
                "swot",
            ]
            if any(term in microbook_lower for term in forbidden_modernization_terms) and attempt < 4:
                guidance = (
                    "A versão expandida introduziu termos específicos (mercado/marketing/concorrência ou SWOT). "
                    "Reescreva mantendo aplicações genéricas e marcadores de aplicação contemporânea."
                )
                continue

            sanitized = self._sanitize_microbook_markdown(expanded.microbook_markdown)
            return expanded.model_copy(update={"microbook_markdown": sanitized})

        raise ValueError("Falha inesperada ao expandir o microbook.")
