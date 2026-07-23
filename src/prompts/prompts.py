from __future__ import annotations

import json
from textwrap import dedent

from domain.configurations import AppConfig
from domain.models import EditorialKnowledgeMap, EditorialOutput, ReviewReport, SourceDocument


EDITORIAL_SYSTEM_PROMPT = dedent(
    """
    Você é um agente editorial criterioso.
    Sua obrigação é preservar fidelidade ao material-fonte.
    Não invente fatos históricos, bibliográficos ou interpretações como se fossem fatos.
    Responda apenas em JSON válido.
    """
).strip()


REVIEW_SYSTEM_PROMPT = dedent(
    """
    Você é um revisor editorial rigoroso.
    Compare a saída com a fonte e a configuração.
    Aponte extrapolações e trate o modelo gerador como falível.
    Responda apenas em JSON válido.
    """
).strip()


DISTRIBUTION_SYSTEM_PROMPT = dedent(
    """
    Você é um agente de distribuição de conteúdo.
    Adapte a ideia central com fidelidade, clareza e adequação ao formato.
    Não copie o microbook literalmente.
    Responda apenas em JSON válido.
    """
).strip()


IDEA_MAP_SYSTEM_PROMPT = dedent(
    """
    Você é um analista editorial.
    Antes da escrita, sua função é transformar o material-fonte em um mapa estruturado de ideias.
    Não invente ideias nem referências de origem.
    Responda apenas em JSON válido.
    """
).strip()


EDITORIAL_EXPANSION_SYSTEM_PROMPT = dedent(
    """
    Você é um editor responsável por expandir um microbook sem perder fidelidade.
    Preserve o briefing já definido.
    Reescreva o microbook para atingir o intervalo pedido de palavras.
    Não invente fatos e responda apenas em JSON válido.
    """
).strip()


def build_editorial_prompt(
    config: AppConfig,
    source: SourceDocument,
    idea_map: EditorialKnowledgeMap,
    extra_guidance: str = "",
) -> str:
    guidance_block = f"\nOrientação adicional:\n- {extra_guidance}\n" if extra_guidance else ""

    return dedent(
        f"""
        Gere um JSON com a seguinte estrutura:
        {{
          "briefing": {{
            "target_audience": "...",
            "promised_transformation": "...",
            "must_have_ideas": ["...", "...", "...", "...", "..."],
            "tone_of_voice": "...",
            "tone_rationale": "..."
          }},
          "microbook_title": "...",
          "microbook_markdown": "..."
        }}

        Regras:
        - O microbook deve ter entre {config.generation.microbook_min_words} e {config.generation.microbook_max_words} palavras.
        - Mire aproximadamente 900 palavras.
        - Nao finalize com menos de {config.generation.microbook_min_words} palavras.
        - Se perceber que o texto ainda esta curto, continue desenvolvendo antes de encerrar.
        - Baseie-se no material-fonte.
        - Desenvolva cinco ideias centrais.
        - Escreva em português.
        - Evite afirmações não sustentadas pelo texto.
        - Diferencie com clareza o que vem da obra e o que é aplicação contemporânea.
        - Não trate guerra como metáfora direta para negócios, mercado ou marketing.
        - Evite exemplos específicos de marketing, concorrência e “sobrevivência empresarial”; prefira aplicações genéricas (decisões de alto impacto, leitura de contexto, prioridade, recursos e consequências).
        - Quando fizer aplicação contemporânea, use marcadores explícitos como "Em uma aplicação contemporânea," e não atribua a aplicação ao autor.
        - Use Markdown apenas dentro do campo microbook_markdown.
        - microbook_markdown deve começar diretamente em "## Introdução"; não repita o título dentro do corpo.
        - Estruture o microbook com:
          1. introdução;
          2. cinco seções principais, uma para cada ideia central;
          3. conclusão.
        - Faça a introdução ter aproximadamente 90 a 120 palavras.
        - Faça cada seção principal ter aproximadamente 120 a 150 palavras.
        - Faça a conclusão ter aproximadamente 70 a 100 palavras.
        - Não entregue resumo curto. Desenvolva explicação, contexto e implicação prática em cada seção.
        - Evite encerrar se alguma seção estiver subdesenvolvida ou muito resumida.

        Metadados fixos:
        - Título: {config.book.title}
        - Autor: {config.book.author}
        - Ano/rótulo temporal: {config.book.publication_label}

        Parâmetros editoriais:
        - Público-alvo: {config.editorial.target_audience}
        - Transformação prometida: {config.editorial.promised_transformation}
        - Tom de voz preferencial: {config.editorial.tone_of_voice}
        - Regras editoriais: {config.editorial.editorial_rules}
        {guidance_block}

        Mapa estruturado de ideias:
        {format_idea_map_for_prompt(idea_map)}

        Material-fonte:
        {source.as_prompt_context(config.generation.max_source_chars)}
        """
    ).strip()


def build_idea_map_prompt(config: AppConfig, source: SourceDocument, extra_guidance: str = "") -> str:
    guidance_block = f"\nOrientação adicional:\n- {extra_guidance}\n" if extra_guidance else ""

    return dedent(
        f"""
        Gere um JSON com a estrutura:
        {{
          "book_title": "{config.book.title}",
          "ideas": [
            {{
              "idea_id": "idea_01",
              "title": "...",
              "summary": "...",
              "source_reference": {{
                "page_start": 1,
                "page_end": 2,
                "section_hint": "..."
              }},
              "themes": ["...", "..."],
              "evidence_excerpt": "..."
            }}
          ]
        }}

        Regras:
        - extraia entre 5 e 8 ideias centrais da obra;
        - cada ideia deve ser editorialmente reutilizável;
        - use páginas reais do texto fornecido;
        - section_hint pode usar o título mais próximo disponível no material;
        - evidence_excerpt deve trazer um trecho fiel ao conteúdo carregado, longo o bastante para sustentar a ideia;
        - quando a ideia envolver enumeração (ex.: lista de fatores), inclua no evidence_excerpt a enumeração completa se ela aparecer no texto extraído;
        - evite evidence_excerpt curto demais que não comprove a afirmação do summary;
        - não invente capítulos se eles não estiverem explicitamente visíveis no material.
        {guidance_block}

        Material-fonte:
        {source.as_prompt_context(config.generation.max_source_chars)}
        """
    ).strip()


def format_idea_map_for_prompt(idea_map: EditorialKnowledgeMap) -> str:
    return json.dumps(idea_map.model_dump(), ensure_ascii=False, indent=2)


def build_editorial_expansion_prompt(
    config: AppConfig,
    source: SourceDocument,
    idea_map: EditorialKnowledgeMap,
    editorial: EditorialOutput,
    current_word_count: int,
) -> str:
    return dedent(
        f"""
        Reescreva o conteúdo abaixo em JSON com a mesma estrutura:
        {{
          "briefing": {{
            "target_audience": "...",
            "promised_transformation": "...",
            "must_have_ideas": ["...", "...", "...", "...", "..."],
            "tone_of_voice": "...",
            "tone_rationale": "..."
          }},
          "microbook_title": "...",
          "microbook_markdown": "..."
        }}

        Objetivo:
        - manter o briefing já definido;
        - preservar o núcleo das ideias;
        - expandir o microbook para ficar entre {config.generation.microbook_min_words} e {config.generation.microbook_max_words} palavras;
        - mirar aproximadamente 900 palavras.
        - nao finalize com menos de {config.generation.microbook_min_words} palavras.

        Regras de expansão:
        - mantenha introdução, cinco seções principais e conclusão;
        - mantenha clara a distinção entre texto-fonte e aplicação contemporânea;
        - não trate guerra como metáfora direta para negócios, mercado ou marketing;
        - evite exemplos específicos de marketing, concorrência e “sobrevivência empresarial”; prefira aplicações genéricas (decisões de alto impacto, leitura de contexto, prioridade, recursos e consequências);
        - quando fizer aplicação contemporânea, use marcadores explícitos como "Em uma aplicação contemporânea," e não atribua a aplicação ao autor;
        - microbook_markdown deve começar diretamente em "## Introdução"; não repita o título dentro do corpo;
        - faça a introdução ter aproximadamente 90 a 120 palavras;
        - faça cada seção principal ter aproximadamente 120 a 150 palavras;
        - faça a conclusão ter aproximadamente 70 a 100 palavras;
        - aprofunde explicação, contexto e implicação prática;
        - não invente fatos;
        - não reduza o conteúdo;
        - escreva em português e em Markdown apenas dentro de microbook_markdown.

        Briefing atual:
        {json.dumps(editorial.briefing.model_dump(), ensure_ascii=False, indent=2)}

        Mapa estruturado de ideias:
        {format_idea_map_for_prompt(idea_map)}

        Título atual:
        {editorial.microbook_title}

        Microbook atual ({current_word_count} palavras):
        {editorial.microbook_markdown}

        Material-fonte:
        {source.as_prompt_context(config.generation.max_source_chars)}
        """
    ).strip()


def build_review_prompt(
    config: AppConfig,
    source: SourceDocument,
    idea_map: EditorialKnowledgeMap,
    editorial: EditorialOutput,
    extra_guidance: str = "",
) -> str:
    guidance_block = f"\nOrientação adicional:\n- {extra_guidance}\n" if extra_guidance else ""
    return dedent(
        f"""
        Revise o conteúdo abaixo e gere um JSON com a seguinte estrutura:
        {{
          "verdict": "...",
          "adherence_summary": "...",
          "strengths": ["..."],
          "possible_unsupported_claims": ["..."],
          "must_fix": ["..."],
          "minor_edits": ["..."],
          "traceability_items": [
            {{
              "claim": "...",
              "classification": "Citação direta | Paráfrase fiel | Interpretação consistente | Aplicação contemporânea | Requer verificação | Não possui correspondência clara",
              "source_ideas": ["idea_01"],
              "source_reference": "páginas 2-3, seção ...",
              "observation": "trecho analisado + problema identificado + ação recomendada"
            }}
          ],
          "kept_example": {{"content": "...", "reason": "..."}},
          "modified_example": {{"content": "...", "reason": "..."}},
          "rejected_example": {{"content": "...", "reason": "..."}}
        }}

        Critérios:
        - fidelidade ao material-fonte;
        - aderência ao mapa estruturado de ideias;
        - coerência;
        - cumprimento do briefing;
        - adequação ao público;
        - tom de voz;
        - possíveis informações não sustentadas.
        - Para cada item em traceability_items, relacione a afirmação com o mapa editorial e classifique com precisão se ela é citação direta, paráfrase fiel, interpretação consistente, aplicação contemporânea, requer verificação ou não possui correspondência clara.
        - Em observation, cite o trecho analisado, diga qual é o problema ou acerto e indique a ação editorial recomendada.
        - Não tente validar cada frase do microbook; selecione de 3 a 5 afirmações representativas.
        - Evite observações genéricas. Seja específico sobre seção, trecho e tipo de ajuste.
        - Citação direta só é permitida quando a frase aparece literalmente no material-fonte carregado; caso contrário use Paráfrase fiel.
        - Se a afirmação for uma aplicação para contextos atuais, marque como Aplicação contemporânea e recomende explicitar esse enquadramento no microbook.
        - Para cada item, sugira uma ação clara: Manter | Reformular | Rejeitar.
        - Não use como "afirmação" um enunciado do tipo "Em uma aplicação contemporânea...". Escolha uma afirmação do texto do microbook e classifique a ponte contemporânea na observação.

        Configuração:
        - Público-alvo: {config.editorial.target_audience}
        - Transformação prometida: {config.editorial.promised_transformation}
        - Tom de voz: {config.editorial.tone_of_voice}

        Briefing gerado:
        {json.dumps(editorial.briefing.model_dump(), ensure_ascii=False, indent=2)}

        Mapa estruturado de ideias:
        {format_idea_map_for_prompt(idea_map)}

        Microbook gerado:
        {editorial.microbook_markdown}

        Material-fonte:
        {source.as_prompt_context(config.generation.max_source_chars)}
        {guidance_block}
        """
    ).strip()


def build_distribution_prompt(
    config: AppConfig,
    idea_map: EditorialKnowledgeMap,
    editorial: EditorialOutput,
    review: ReviewReport,
    extra_guidance: str = "",
) -> str:
    guidance_block = f"\nOrientação adicional:\n- {extra_guidance}\n" if extra_guidance else ""
    return dedent(
        f"""
        Gere um JSON com a estrutura:
        {{
          "scripts": [
            {{
              "approach": "educacional",
              "hook": "...",
              "development": "...",
              "visual_suggestion": "...",
              "call_to_action": "...",
              "priority_platform": "Instagram Reels",
              "platform_rationale": "..."
            }},
            {{
              "approach": "contrario_ou_provocativo",
              "hook": "...",
              "development": "...",
              "visual_suggestion": "...",
              "call_to_action": "...",
              "priority_platform": "Instagram Reels",
              "platform_rationale": "..."
            }},
            {{
              "approach": "ugc",
              "hook": "...",
              "development": "...",
              "visual_suggestion": "...",
              "call_to_action": "...",
              "priority_platform": "Instagram Reels",
              "platform_rationale": "..."
            }}
          ]
        }}

        Regras:
        - Os três roteiros devem ter abordagens diferentes.
        - Preserve a ideia central do microbook.
        - Não copie o texto literalmente.
        - Respeite o público-alvo.
        - Explique por que Instagram Reels é adequado a cada roteiro.
        - O roteiro educacional deve ensinar algo imediatamente aplicável.
        - O roteiro provocativo deve quebrar uma crença comum de forma memorável.
        - O roteiro UGC deve soar como relato pessoal espontâneo, não como campanha institucional.
        - Evite frases genéricas de marketing e CTA vazia.
        - Cada development deve ser autocontido, com começo-meio-fim e uma ideia aplicável em 20-35s.
        - Não use “metáfora para negócios” nem “guerra nos negócios” como fórmula. Se houver aplicação contemporânea, marque como leitura editorial sem atribuir ao autor.
        - Diferencie as justificativas de plataforma:
          - Educacional: favorece checklist visual e salvamentos.
          - Provocativo: favorece ganchos de contraste e comentários.
          - UGC: favorece narrativa pessoal e identificação.

        Modelo de qualidade (siga o estilo, não copie literalmente):
        - Educacional: gancho com 3 perguntas + checklist + CTA de salvar.
        - Provocativo: “precisa mesmo entrar nessa?” + ideia de evitar desgaste + CTA de comentar.
        - UGC: relato pessoal “eu parei antes de agir” + insight “movimento não é progresso” + CTA de seguir.

        Público-alvo:
        {config.editorial.target_audience}

        Mapa estruturado de ideias:
        {format_idea_map_for_prompt(idea_map)}

        Microbook:
        {editorial.microbook_markdown}

        Síntese da revisão:
        {review.adherence_summary}
        {guidance_block}
        """
    ).strip()
