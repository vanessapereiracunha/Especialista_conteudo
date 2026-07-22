# Plano Técnico e Arquitetura

## 1. Decisão central
A solução separa o que precisa ser controlado deterministicamente pelo código do que pode ser delegado ao modelo de linguagem. Metadados, estrutura dos arquivos, renderização, validações e persistência ficam em Python. Geração editorial, adaptação de linguagem e revisão crítica orientada por prompt ficam no LLM.

## 2. Decisão sobre RAG
Não será usado RAG nesta versão.

### Justificativa
- O material-fonte fornecido possui 37 páginas e tamanho reduzido.
- O custo operacional de vetorizar, indexar e recuperar trechos não é proporcional ao escopo do teste.
- O risco principal aqui é editorial, não de escala.
- A fidelidade será tratada com:
  - extração integral do texto;
  - prompts ancorados na fonte;
  - etapa explícita de revisão;
  - validações e relatório de achados.

## 3. Arquitetura em camadas

### Application Layer
Orquestra a sequência da pipeline:
1. carregar configuração;
2. carregar a fonte;
3. gerar briefing e microbook;
4. revisar;
5. gerar distribuição;
6. salvar artefatos.

Arquivo principal:
- `src/application/content_pipeline.py`

### Agent Layer
Encapsula prompts e parsing de respostas:
- `idea_mapper_agent.py`
- `editorial_agent.py`
- `review_agent.py`
- `distribution_agent.py`

### Domain Layer
Modelos tipados e regras de validação:
- `models.py`
- `configurations.py`

### Infrastructure Layer
Integrações com mundo externo:
- `llm_client.py`
- `source_loader.py`
- `file_repository.py`

### Prompt Layer
Centraliza instruções reutilizáveis:
- `prompts.py`

## 4. Fluxo da pipeline
1. Ler `config/editorial.yaml`.
2. Validar metadados obrigatórios.
3. Extrair texto do arquivo-fonte (`.pdf` ou `.txt`).
4. Montar contexto textual com marcação por página.
5. Solicitar ao LLM um mapa estruturado de ideias com origem e temas.
6. Solicitar ao LLM um JSON estruturado para briefing + microbook usando o mapa editorial.
7. Validar campos e contagem de palavras.
8. Solicitar revisão crítica com base na fonte, no briefing e no mapa editorial.
9. Solicitar três roteiros a partir do microbook revisado e do mapa editorial.
10. Renderizar Markdown final e persistir o JSON do mapa de ideias.

## 5. Responsabilidades dos módulos

### `content_pipeline.py`
- coordena as etapas;
- gera erros claros;
- decide ordem de persistência.

### `idea_mapper_agent.py`
- extrai ideias centrais reutilizáveis;
- registra origem aproximada no material;
- produz a base editorial estruturada usada pelas etapas seguintes.

### `editorial_agent.py`
- constrói prompt editorial;
- solicita saída estruturada com base no mapa editorial;
- converte JSON em modelo tipado.

### `review_agent.py`
- avalia aderência ao briefing;
- identifica possíveis extrapolações;
- registra conteúdo mantido, modificado e rejeitado.

### `distribution_agent.py`
- adapta o microbook em três roteiros;
- garante campos obrigatórios por roteiro.
- preserva a aderência ao mapa editorial.

### `llm_client.py`
- abstrai o provedor;
- permite troca por compatível com OpenAI via HTTP.

### `source_loader.py`
- lê PDF/TXT;
- mantém divisão por páginas;
- entrega texto completo para grounding.

### `file_repository.py`
- grava Markdown;
- cria pastas quando necessário.

## 6. Estrutura de diretórios
```text
project/
├── .specify/
│   └── memory/
│       └── constitution.md
├── config/
│   └── editorial.yaml
├── data/
│   └── source/
│       └── a_arte_da_guerra.pdf
├── docs/
│   ├── distribution-agent/
│   │   └── README.md
│   └── editorial-agent/
│       └── README.md
├── output/
│   ├── editorial_ideas.json
│   ├── editorial.md
│   ├── review.md
│   ├── distribution.md
│   └── operacao_editorial.md
├── specs/
│   ├── acceptance-criteria.md
│   ├── architecture.md
│   ├── requirements.md
│   └── tasks.md
├── src/
│   ├── agents/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── prompts/
├── tests/
├── .env.example
├── README.md
└── requirements.txt
```

## 7. Tecnologias
- Python 3.11+
- Pydantic
- PyYAML
- requests
- pypdf
- pytest

## 8. Estratégia de testes
- validar leitura de configuração;
- validar contagem de palavras;
- validar renderização e campos obrigatórios;
- testar parsing de modelos determinísticos;
- executar smoke test do carregador de fonte.

## 9. Estratégia de configuração
- valores editoriais no YAML;
- credenciais do provedor em variáveis de ambiente;
- caminhos relativos ao projeto;
- defaults conservadores no cliente do LLM.

## 10. Estratégia de uso do LLM
- prompts separados por responsabilidade;
- pedido de JSON estruturado para facilitar parsing;
- camada intermediária de conhecimento editorial em JSON antes da geração do microbook;
- revisão como etapa distinta, não embutida na geração;
- sem delegar metadados fixos ao modelo.

## 11. Divergências aceitáveis
- Se o PDF não expuser ano editorial exato, a configuração usa rótulo temporal confiável da obra com nota de fonte.
- Se não houver credenciais de LLM no ambiente, o código continua executável até a etapa que depende do modelo e falha com orientação explícita.
