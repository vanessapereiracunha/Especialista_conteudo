from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
SRC_ROOT = CURRENT_FILE.parents[1]
PROJECT_ROOT = CURRENT_FILE.parents[2]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.distribution_agent import DistributionAgent
from agents.editorial_agent import EditorialAgent
from agents.idea_mapper_agent import IdeaMapperAgent
from agents.review_agent import ReviewAgent
from application.validators import count_words, ensure_range
from domain.configurations import AppConfig, load_config
from domain.models import DistributionOutput, EditorialKnowledgeMap, EditorialOutput, ReviewReport
from infrastructure.file_repository import FileRepository
from infrastructure.llm_client import build_llm_client
from infrastructure.source_loader import SourceLoader


def log_step(message: str) -> None:
    print(f"[PIPELINE] {message}", flush=True)


def render_ideas_map_json(idea_map: EditorialKnowledgeMap) -> str:
    return json.dumps(idea_map.model_dump(), ensure_ascii=False, indent=2)


def render_editorial_markdown(
    config: AppConfig,
    idea_map: EditorialKnowledgeMap,
    editorial: EditorialOutput,
) -> str:
    ideas = "\n".join(f"{index}. {idea}" for index, idea in enumerate(editorial.briefing.must_have_ideas, start=1))
    mapped_ideas = "\n".join(
        f"- **{idea.idea_id} — {idea.title}:** {idea.summary} "
        f"(origem: páginas {idea.source_reference.page_start}-{idea.source_reference.page_end}, "
        f"seção: {idea.source_reference.section_hint})"
        for idea in idea_map.ideas
    )
    return f"""# Conteúdo Editorial

## Briefing Editorial

### Metadados
- **Título:** {config.book.title}
- **Autor:** {config.book.author}
- **Ano / referência temporal:** {config.book.publication_label}

### Público-alvo
{editorial.briefing.target_audience}

### Transformação prometida
{editorial.briefing.promised_transformation}

### Cinco ideias que não podem faltar
{ideas}

### Tom de voz
{editorial.briefing.tone_of_voice}

### Justificativa do tom de voz
{editorial.briefing.tone_rationale}

## Mapa Estruturado de Ideias
O mapa editorial abaixo identificou {len(idea_map.ideas)} ideias centrais da obra. Para este microbook, cinco delas foram priorizadas por aderência ao público-alvo e à transformação proposta.

{mapped_ideas}

## Microbook

### {editorial.microbook_title}

{editorial.microbook_markdown}
"""


def render_review_markdown(review: ReviewReport) -> str:
    strengths = "\n".join(f"- {item}" for item in review.strengths) or "- Nenhum item registrado."
    unsupported = "\n".join(f"- {item}" for item in review.possible_unsupported_claims) or "- Nenhum item identificado."
    must_fix = "\n".join(f"- {item}" for item in review.must_fix) or "- Nenhum ajuste obrigatório."
    minor_edits = "\n".join(f"- {item}" for item in review.minor_edits) or "- Nenhum ajuste menor."
    evidence_items = [
        item
        for item in review.traceability_items
        if item.classification.strip().lower() in {"citação direta", "paráfrase fiel"}
        and item.source_reference.strip()
        and not item.claim.strip().lower().startswith("em uma aplicação contempor")
    ]
    evidence_summary = (
        "\n".join(f"- {item.claim} ({item.source_reference})" for item in evidence_items[:5]) or strengths
    )
    traceability_items = "\n".join(
        "\n".join(
            [
                f"- **Afirmação:** {item.claim}",
                f"  - **Classificação:** {item.classification}",
                f"  - **Ideias de origem:** {', '.join(item.source_ideas) if item.source_ideas else 'Não informado'}",
                f"  - **Referência:** {item.source_reference}",
                f"  - **Observação:** {item.observation}",
            ]
        )
        for item in review.traceability_items
    ) or "- Nenhum item de rastreabilidade registrado."

    return f"""# Revisão Editorial

## Veredito
{review.verdict}

## Síntese de aderência
{review.adherence_summary}

## Evidências explícitas da fonte
{evidence_summary}

## Pontos fortes
{strengths}

## Possíveis afirmações sem sustentação
{unsupported}

## Ajustes obrigatórios
{must_fix}

## Ajustes menores
{minor_edits}

## Rastreabilidade da revisão
{traceability_items}

## Exemplo mantido
- **Conteúdo:** {review.kept_example.content}
- **Motivo:** {review.kept_example.reason}

## Exemplo modificado
- **Conteúdo:** {review.modified_example.content}
- **Motivo:** {review.modified_example.reason}

## Exemplo rejeitado
- **Conteúdo:** {review.rejected_example.content}
- **Motivo:** {review.rejected_example.reason}
"""


def render_distribution_markdown(distribution: DistributionOutput) -> str:
    sections = ["# Distribuição e UGC"]
    for index, script in enumerate(distribution.scripts, start=1):
        sections.append(
            f"""## Roteiro {index} — {script.approach}

- **Gancho inicial:** {script.hook}
- **Desenvolvimento:** {script.development}
- **Indicação visual / cena:** {script.visual_suggestion}
- **CTA:** {script.call_to_action}
- **Plataforma prioritária:** {script.priority_platform}
- **Justificativa da plataforma:** {script.platform_rationale}
"""
        )
    return "\n".join(sections)


def render_operational_response() -> str:
    return """# Operação Editorial

Eu reorganizaria o trabalho a partir do risco editorial. A prioridade imediata seria validar as duas informações possivelmente inventadas, porque qualquer erro de fidelidade compromete o microbook e também os roteiros que derivam dele.

As duas afirmações prioritárias para verificação são:
1. a recomendação de que a avaliação deve ser cultivada como “um hábito” para qualquer profissional;
2. a interpretação de que o princípio do engano equivale diretamente a “adaptação e inovação”.

Eu verificaria primeiro se essas informações estão de fato sustentadas pela fonte e em quais peças elas aparecem. Se estiverem só em trechos específicos, eu congelaria apenas essas partes. Eu não esperaria a correção das duas informações para iniciar as tarefas que não dependem delas. Em paralelo, manteria revisão estrutural, preparação de publicação e tudo o que não depende dos pontos sob dúvida.

Ao mesmo tempo, eu replanejaria o UGC para absorver o atraso de um dia sem travar a sexta-feira. As pessoas que precisam ser informadas imediatamente são revisão, liderança editorial, responsável por distribuição/UGC e quem fará a publicação.

Para reduzir recorrência, eu ajustaria o processo com uma etapa obrigatória de checagem de afirmações sensíveis antes da aprovação final, marcando com clareza o que veio da fonte, o que é interpretação editorial e o que exige confirmação adicional.
"""


def run_pipeline(config_path: str | Path = PROJECT_ROOT / "config" / "editorial.yaml") -> None:
    started_at = time.perf_counter()
    config = load_config(config_path)
    source_path = PROJECT_ROOT / config.book.source_path
    repository = FileRepository()

    log_step("Carregando material-fonte...")
    source = SourceLoader().load(source_path)
    log_step(f"Fonte carregada com {len(source.pages)} páginas.")

    log_step("Inicializando cliente do LLM...")
    llm_client = build_llm_client(config.llm.provider)

    log_step("Gerando mapa estruturado de ideias...")
    idea_map = IdeaMapperAgent(llm_client, config).run(source)
    repository.write_text(PROJECT_ROOT / config.output.ideas_map_file, render_ideas_map_json(idea_map))
    log_step("Mapa de ideias salvo em output/editorial_ideas.json.")

    editorial_agent = EditorialAgent(llm_client, config)
    log_step("Gerando briefing editorial e microbook...")
    editorial = editorial_agent.run(source, idea_map)
    word_count = count_words(editorial.microbook_markdown)
    repository.write_text(PROJECT_ROOT / config.output.editorial_file, render_editorial_markdown(config, idea_map, editorial))
    log_step(f"Saída editorial parcial salva com {word_count} palavras.")

    for attempt in range(3):
        if config.generation.microbook_min_words <= word_count <= config.generation.microbook_max_words:
            break

        log_step(
            f"Microbook fora do intervalo ({word_count} palavras). Executando expansão {attempt + 1}/3..."
        )
        editorial = editorial_agent.expand_microbook(source, idea_map, editorial, word_count)
        word_count = count_words(editorial.microbook_markdown)
        repository.write_text(PROJECT_ROOT / config.output.editorial_file, render_editorial_markdown(config, idea_map, editorial))
        log_step(f"Microbook atualizado para {word_count} palavras.")

    ensure_range(
        word_count,
        config.generation.microbook_min_words,
        config.generation.microbook_max_words,
        "Microbook",
    )

    log_step("Executando revisão editorial...")
    review = ReviewAgent(llm_client, config).run(source, idea_map, editorial)
    repository.write_text(PROJECT_ROOT / config.output.review_file, render_review_markdown(review))
    log_step("Relatório de revisão salvo.")

    log_step("Gerando roteiros de distribuição...")
    distribution = DistributionAgent(llm_client, config).run(idea_map, editorial, review)
    repository.write_text(PROJECT_ROOT / config.output.distribution_file, render_distribution_markdown(distribution))
    repository.write_text(PROJECT_ROOT / config.output.operations_file, render_operational_response())
    log_step("Roteiros e resposta operacional salvos.")

    log_step(f"Pipeline concluída em {time.perf_counter() - started_at:.1f}s.")


if __name__ == "__main__":
    run_pipeline()
