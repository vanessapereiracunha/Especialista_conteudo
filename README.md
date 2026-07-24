# Teste Técnico — Especialista de Conteúdo

## Visão geral
Este projeto implementa uma pipeline editorial assistida por IA para transformar a obra **A Arte da Guerra**, de **Sun Tzu**, em:
- briefing editorial;
- microbook;
- revisão crítica;
- três roteiros de Instagram Reels;
- resposta de operação editorial;
- registro transparente do uso de IA.

O projeto foi estruturado com **Spec-Driven Development (SDD)**: primeiro constituição, requisitos, plano, critérios de aceitação e tarefas; depois implementação e validação.

O Spec Kit foi usado apenas para estruturar requisitos e critérios de aceitação. O trabalho principal foi transformar isso em uma pipeline executável, com contratos, validação, rastreabilidade e revisão.

## Leitura rápida
Para avaliar a entrega com rapidez, esta é a melhor ordem de leitura:
- `specs/requirements.md`: o que a solução precisava cobrir;
- `specs/architecture.md`: como o escopo foi traduzido em arquitetura;
- `src/application/content_pipeline.py`: onde a pipeline é orquestrada;
- `output/editorial.md`: briefing + microbook;
- `output/review.md`: revisão crítica e registro de decisões;
- `output/distribution.md`: adaptação para três roteiros;
- `output/ai_usage.md`: transparência do uso de IA.

## Objetivo
Demonstrar capacidade de:
- orientar modelos de linguagem;
- revisar criticamente saídas geradas por IA;
- preservar fidelidade ao material-fonte;
- transformar uma mesma ideia em formatos editoriais diferentes;
- manter simplicidade técnica e clareza de decisão.

## O que esta solução demonstra
- **uso consciente de IA**: a IA gera conteúdo, mas não define metadados fixos nem valida a si mesma sozinha;
- **qualidade editorial**: briefing, microbook e roteiros foram escritos com público, tom e objetivo claros;
- **revisão crítica**: a pipeline explicita conteúdo mantido, modificado e rejeitado;
- **fidelidade ao material-fonte**: a obra é carregada diretamente do PDF fornecido, com revisão dedicada a extrapolações;
- **organização técnica**: camadas enxutas, configuração externa, modelos tipados e testes nas partes determinísticas;
- **camada editorial intermediária**: antes da geração, a pipeline cria um mapa estruturado de ideias com origem e temas, usado para orientar escrita e revisão.

## Estrutura do projeto
```text
.specify/memory/constitution.md
specs/
config/editorial.yaml
data/source/a_arte_da_guerra.pdf
src/
tests/
docs/
output/
README.md
requirements.txt
.env.example
```

## Arquitetura
Arquitetura modular em quatro camadas:
- **Application Layer**: orquestra a pipeline.
- **Agent Layer**: geração editorial, revisão e distribuição.
- **Domain Layer**: modelos tipados e configuração.
- **Infrastructure Layer**: LLM, fonte e persistência.

Essa divisão foi escolhida para manter o projeto simples, mas com separação suficiente para trocar o provedor de LLM, adaptar o pipeline para outro livro e testar as partes determinísticas sem acoplar tudo a uma única função.

## Fluxo da pipeline
1. Ler configuração em YAML.
2. Carregar o PDF da obra.
3. Extrair texto por página.
4. Gerar um mapa estruturado de ideias com origem e temas.
5. Gerar briefing + microbook a partir desse mapa.
6. Validar estrutura e contagem de palavras.
7. Revisar criticamente a saída contra fonte e mapa editorial.
8. Gerar roteiros de distribuição.
9. Persistir artefatos em Markdown e JSON.

## Aderência ao enunciado
- **Constitution**: `.specify/memory/constitution.md`
- **Specify**: `specs/requirements.md` e `specs/acceptance-criteria.md`
- **Plan**: `specs/architecture.md`
- **Tasks**: `specs/tasks.md`
- **Implement**: `src/`
- **Validate**: `tests/` e `output/review.md`

## Fonte e referência bibliográfica
- **Material-fonte principal**: `data/source/a_arte_da_guerra.pdf`
- **Tamanho processado**: 37 páginas extraídas localmente
- **Referência temporal adotada**: obra tradicionalmente atribuída ao século V a.C., com nota de que o texto é provavelmente compilado no início do Período dos Reinos Combatentes
- **Base confiável usada para esse enquadramento temporal**: Encyclopaedia Britannica, verbete sobre Sun Tzu e *The Art of War*

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Variáveis de ambiente
Copie `.env.example` para `.env` ou configure manualmente:
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_TIMEOUT_SECONDS`

Parâmetros avançados de retry e limite de saída podem ser ajustados no `.env.example`, mas não são necessários para entender ou executar o fluxo básico.

### Exemplo com Groq
O cliente do projeto foi preparado para provedores compatíveis com a API da OpenAI.  
Para usar **Groq**, um exemplo funcional é:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=sua_chave_do_provedor_aqui
LLM_MODEL=llama-3.3-70b-versatile
LLM_TIMEOUT_SECONDS=90
```

Esse formato funciona bem para o fluxo atual. O cliente também pode ser adaptado para outros provedores compatíveis.

## Execução

```bash
python -m src.main
pytest
```

`pytest` valida rapidamente as partes determinísticas do projeto. Já `python -m src.main` executa a pipeline completa com IA: mapeamento editorial, geração do microbook, revisão e adaptação para roteiros. O tempo total depende do provedor de LLM, do modelo escolhido e da latência externa da API.

Durante a execução completa, a pipeline imprime a etapa atual no terminal e salva artefatos intermediários em `output/` assim que cada fase conclui. Isso reduz a sensação de travamento e permite inspecionar progresso parcial mesmo se a etapa seguinte falhar no provedor.

### Exemplo de execução no PowerShell

```powershell
$env:LLM_BASE_URL="https://api.groq.com/openai/v1"
$env:LLM_API_KEY="SUA_CHAVE_DO_PROVEDOR"
$env:LLM_MODEL="llama-3.3-70b-versatile"
$env:LLM_TIMEOUT_SECONDS="90"
python -m src.main
```

## Exemplo de uso
O pipeline usa `config/editorial.yaml` e lê a fonte em `data/source/a_arte_da_guerra.pdf`.  
As saídas são gravadas em `output/`.
Os arquivos já presentes em `output/` funcionam como artefatos de entrega e também como referência de qualidade para quem quiser avaliar o projeto sem depender de uma nova execução completa do LLM.

## Saídas da entrega
- `output/editorial_ideas.json`: mapa estruturado de ideias com origem e temas;
- `output/editorial.md`: Parte 1, com briefing editorial e microbook;
- `output/distribution.md`: Parte 2, com três roteiros de Reels;
- `output/operacao_editorial.md`: Parte 3, com reorganização operacional;
- `output/review.md`: revisão crítica explícita;
- `output/ai_usage.md`: registro do uso de IA.

Para a submissão final, o conteúdo de `output/operacao_editorial.md` deve ser copiado para um Google Docs e o link incluído junto da entrega.

## Documentação complementar
- `docs/editorial-agent/README.md`: explica entradas, saídas, limites e uso de IA no agente editorial;
- `docs/distribution-agent/README.md`: explica como o microbook é transformado em roteiros e como a fidelidade é preservada.

## Decisões de engenharia
### Separação entre determinístico e generativo
Metadados fixos do livro, estrutura dos arquivos, contagem de palavras, validações e persistência são controlados por Python.  
Briefing, microbook, roteiros e revisão argumentativa são delegados ao LLM.

### Mapa Estruturado de Ideias
Em vez de gerar o microbook diretamente do texto bruto, a pipeline cria antes um **Mapa Estruturado de Ideias**. Essa camada intermediária organiza ideias centrais da obra com referência de origem, temas e evidência textual. O microbook e os roteiros passam a ser derivados dessa base editorial, o que melhora rastreabilidade, reaproveitamento e revisão crítica.

### Decisão sobre RAG
**Não foi utilizado RAG por decisão de arquitetura, não por omissão.** O material-fonte efetivamente fornecido no teste é curto o suficiente para ser processado integralmente com boa rastreabilidade. Neste escopo, a principal necessidade não era recuperar trechos em um corpus extenso, mas estruturar editorialmente a obra antes da geração. Por isso, a solução adotou um **Mapa Estruturado de Ideias** como camada intermediária, com origem, temas e evidências textuais, usado depois na escrita, na revisão e na adaptação para distribuição.

Nesse contexto, introduzir recuperação vetorial aumentaria a complexidade sem ganho proporcional de fidelidade ou controle editorial. Para um cenário comercial com obras muito maiores, múltiplas fontes ou acervo contínuo, a evolução natural desta arquitetura seria combinar **recuperação guiada** com a mesma camada editorial intermediária. Em outras palavras: aqui o mapa substitui a necessidade de RAG no escopo do teste, mas não impede a solução de evoluir para RAG quando o problema real passar a exigir recuperação seletiva.

Essa escolha também preserva viabilidade comercial no curto prazo: mesmo sem RAG, a pipeline já demonstra um fluxo reutilizável de **fonte -> estruturação editorial -> geração -> revisão -> distribuição**, com controle, rastreabilidade e possibilidade de escalar o processo antes de escalar a infraestrutura.

### Troca de provedor
A lógica dos agentes depende apenas da interface `LLMClient`. Assim, a troca de provedor fica isolada em `src/infrastructure/llm_client.py`.

## Uso de IA
O uso de IA foi intencional e explícito:
- geração do briefing;
- geração do microbook;
- revisão crítica assistida;
- adaptação para roteiros;
- apoio na redação e refino dos artefatos.

Os detalhes estão em `output/ai_usage.md`.

## Prompts importantes
Os prompts-base vivem em `src/prompts/prompts.py`. Três exemplos centrais:

1. Prompt editorial pedindo JSON estruturado com briefing e microbook, ancorado na fonte.
2. Prompt de revisão tratando a saída do modelo como falível e exigindo itens mantidos, modificados e rejeitados.
3. Prompt de distribuição adaptando a ideia central para três abordagens de Reels sem copiar o texto-base.

## Exemplo de saída revisada
Ver `output/review.md`, que registra:
- conteúdo mantido;
- conteúdo modificado;
- conteúdo rejeitado;
- justificativas.

## Estratégia de fidelidade
- fonte carregada diretamente do PDF fornecido;
- metadados fixos fora do LLM;
- prompts ancorados no texto extraído;
- revisão explícita após geração;
- sinalização de possíveis afirmações sem sustentação.

## Validação executada
- `10` testes automatizados com `pytest` nas partes determinísticas e nos contratos de saída;
- smoke test da extração do PDF;
- validação de contagem do microbook final dentro do intervalo pedido;
- validação estrutural dos modelos tipados.

## Limitações
- A publicação em Google Docs não foi automatizada neste ambiente.
- Sem credenciais válidas de LLM, o pipeline falha apenas na etapa generativa.
- Como a obra é clássica, o campo temporal foi tratado como **rótulo temporal confiável**, não como ano editorial exato da edição, porque o PDF não expõe metadados bibliográficos completos de forma inequívoca.
- O conteúdo final em `output/` foi preparado como entrega local em Markdown; a etapa de publicação externa ficaria fora do escopo deste repositório.

## Melhorias futuras
- adicionar segunda rodada opcional de revisão e reescrita;
- registrar evidências por página de maneira mais granular;
- suportar múltiplas obras por configuração;
- incluir testes de contrato mais amplos para parsing de JSON dos agentes.
