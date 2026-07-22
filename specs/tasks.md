# Tarefas

## T1 - Estruturar especificação e constituição
- **Objetivo:** estabelecer princípios, requisitos, plano técnico e critérios de aceitação.
- **Arquivos:** `.specify/memory/constitution.md`, `specs/*.md`
- **Dependências:** nenhuma
- **Critério de conclusão:** documentação SDD criada e coerente com o desafio.

## T2 - Definir configuração editorial externa
- **Objetivo:** centralizar metadados fixos e parâmetros editoriais em YAML.
- **Arquivos:** `config/editorial.yaml`
- **Dependências:** T1
- **Critério de conclusão:** configuração válida e tipável.

## T3 - Implementar modelos tipados
- **Objetivo:** representar configuração, mapa editorial, briefing, microbook, revisão e roteiros.
- **Arquivos:** `src/domain/models.py`, `src/domain/configurations.py`
- **Dependências:** T2
- **Critério de conclusão:** modelos cobrindo todos os campos obrigatórios.

## T4 - Implementar infraestrutura de fonte e persistência
- **Objetivo:** ler PDF/TXT e salvar arquivos Markdown.
- **Arquivos:** `src/infrastructure/source_loader.py`, `src/infrastructure/file_repository.py`
- **Dependências:** T3
- **Critério de conclusão:** leitura da fonte e gravação de saídas funcionando.

## T5 - Implementar cliente de LLM desacoplado
- **Objetivo:** isolar a integração HTTP com provedor compatível com OpenAI.
- **Arquivos:** `src/infrastructure/llm_client.py`
- **Dependências:** T3
- **Critério de conclusão:** interface única para geração textual com tratamento de erro.

## T6 - Implementar prompts e agentes
- **Objetivo:** separar mapeamento editorial, geração editorial, revisão e distribuição.
- **Arquivos:** `src/prompts/prompts.py`, `src/agents/*.py`
- **Dependências:** T3, T4, T5
- **Critério de conclusão:** agentes retornando modelos tipados a partir de JSON do LLM.

## T7 - Implementar orquestração e validações
- **Objetivo:** coordenar o fluxo completo, persistir o mapa editorial e validar contagem/estrutura.
- **Arquivos:** `src/application/content_pipeline.py`, `src/application/validators.py`
- **Dependências:** T4, T5, T6
- **Critério de conclusão:** pipeline executável até geração dos artefatos.

## T8 - Produzir READMEs e documentação principal
- **Objetivo:** explicar entradas, saídas, arquitetura, limitações e uso de IA.
- **Arquivos:** `README.md`, `docs/editorial-agent/README.md`, `docs/distribution-agent/README.md`, `.env.example`, `requirements.txt`
- **Dependências:** T1 a T7
- **Critério de conclusão:** documentação suficiente para executar e entender decisões.

## T9 - Registrar saídas editoriais e operacionais
- **Objetivo:** entregar conteúdo Markdown da parte editorial, distribuição, revisão, uso de IA e operação editorial.
- **Arquivos:** `output/*.md`
- **Dependências:** T1 a T8
- **Critério de conclusão:** todos os artefatos da entrega local criados.

## T10 - Testar partes determinísticas
- **Objetivo:** verificar configuração, validações e renderização mínima.
- **Arquivos:** `tests/*.py`
- **Dependências:** T3 a T7
- **Critério de conclusão:** testes executando com `pytest`.
