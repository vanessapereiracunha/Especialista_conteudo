# Registro do Uso de IA

## Objetivo do uso de IA
Usei IA para acelerar rascunhos e geração inicial de conteúdo, mas tratei o modelo como falível. O resultado final foi controlado por validações determinísticas, rastreabilidade via mapa estruturado e revisão crítica com decisões explícitas (manter/reformular/rejeitar).

## Sobre Spec Kit / SDD
O Spec Kit foi usado apenas para estruturar requisitos e critérios de aceitação. O trabalho principal foi transformar isso em uma pipeline executável, com contratos, validação, rastreabilidade e revisão.

## Ferramentas utilizadas
- LLM via OpenRouter (modelo: `openai/gpt-4o-mini`): geração do mapa de ideias, microbook, revisão e roteiros.
- Python: orquestração da pipeline, validações e persistência de artefatos.
- `pytest`: testes de contrato (estrutura dos outputs e faixa de palavras).

## Atividades em que a IA foi utilizada (e em quais não)
### IA foi usada para
- gerar um Mapa Estruturado de Ideias (ideias + origem + evidência textual);
- gerar o briefing editorial;
- escrever o microbook dentro do intervalo (800–1000 palavras);
- produzir uma revisão crítica estruturada;
- adaptar para 3 roteiros (educacional / provocativo / UGC).

### IA NÃO foi usada para decidir automaticamente
- estrutura e contratos dos arquivos de saída (`output/*.md`, `output/editorial_ideas.json`);
- critérios de validação (contagem de palavras, presença de seções, consistência);
- decisões de engenharia (camada intermediária do mapa, separação de agentes, quality gates);
- execução e verificação (rodar pipeline e testes).

## Prompts importantes (exemplos)
1) **Mapa editorial (camada intermediária)**

```text
Extraia entre 5 e 8 ideias centrais da obra.
Para cada ideia, registre: idea_id, title, summary, source_reference (page_start/page_end/section_hint), themes e evidence_excerpt.
Não invente capítulos nem referências ausentes.
evidence_excerpt deve ser longo o bastante para sustentar a ideia; se houver enumeração (ex.: cinco fatores), inclua a enumeração completa se estiver no texto.
```

2) **Prompt editorial (briefing + microbook)**

```text
Gere um JSON com briefing e microbook em português.
O microbook deve ter entre 800 e 1000 palavras.
Baseie-se no material-fonte e no mapa estruturado de ideias.
Diferencie com clareza o que vem da obra e o que é aplicação contemporânea.
Não invente fatos históricos/bibliográficos.
```

3) **Prompt de revisão crítica**

```text
Revise comparando microbook, mapa editorial e material-fonte.
Classifique afirmações como: Citação direta / Paráfrase fiel / Interpretação consistente / Aplicação contemporânea / Requer verificação.
Registre itens mantidos, modificados e rejeitados com justificativa e ação (Manter/Reformular/Rejeitar).
```

## Exemplo real de decisão editorial (modificar ou rejeitar)
- **Exemplo rejeitado (por falta de suporte direto):**
  - “A habilidade de avaliar corretamente pode ser a diferença entre o sucesso e o fracasso em qualquer empreendimento.”
  - Motivo: extrapola a formulação do texto-fonte e vira prescrição moderna genérica. Foi marcado como rejeição/reformulação na revisão.

- **Exemplo modificado (para marcar aplicação contemporânea):**
  - Antes: “Sun Tzu começa pela avaliação, não pela ação.”
  - Depois: “No início da obra, Sun Tzu enfatiza a importância de avaliar as condições antes de agir.”
  - Motivo: melhora precisão e evita soar como afirmação literal sobre a obra inteira.

## Como a fidelidade ao material original foi verificada
- processamento do PDF fornecido e uso do texto extraído como base;
- criação do `editorial_ideas.json` com páginas/seções + evidence_excerpt;
- revisão crítica (`review.md`) apontando extrapolações e ações recomendadas;
- validações determinísticas: estrutura dos arquivos e contagem de palavras;
- execução de testes (`pytest`) para garantir contratos dos outputs.
