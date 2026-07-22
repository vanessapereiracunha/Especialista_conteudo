# Especificação de Requisitos

## 1. Objetivo
Entregar uma pipeline editorial em Python, orientada por especificação, que receba uma obra-fonte, gere um briefing editorial, produza um microbook, execute revisão crítica, derive três roteiros para Instagram Reels, registre o uso de IA e documente a lógica operacional do processo.

## 2. Escopo

### Dentro do escopo
- Carregar obra-fonte a partir de `data/source/`.
- Ler configuração editorial externa em YAML.
- Gerar briefing editorial estruturado.
- Gerar microbook em Markdown com 800 a 1.000 palavras.
- Revisar fidelidade, estrutura e aderência ao briefing.
- Gerar três roteiros de Reels com abordagens distintas.
- Produzir resposta objetiva para o cenário de operação editorial.
- Registrar uso de IA, prompts-chave e decisões de revisão.
- Persistir saídas em Markdown.

### Fora do escopo
- Interface web.
- Publicação automática em Google Docs.
- Sistema multiusuário.
- Banco vetorial e RAG sem necessidade comprovada.
- Fluxos assíncronos, filas e observabilidade de produção.

## 3. Entradas
- Arquivo-fonte do livro em `data/source/` (`.pdf` ou `.txt`).
- Configuração editorial em `config/editorial.yaml`.
- Variáveis de ambiente do provedor de LLM.

## 4. Saídas
- `output/editorial_ideas.json`
- `output/editorial.md`
- `output/distribution.md`
- `output/review.md`
- `output/operacao_editorial.md`
- `output/ai_usage.md`

## 5. Requisitos Funcionais

### FR-01 Carregamento da fonte
O sistema deve localizar e carregar o material-fonte configurado.

### FR-02 Tratamento de ausência da fonte
Se o arquivo-fonte não existir, o sistema deve falhar com mensagem clara orientando o uso de `data/source/`.

### FR-03 Configuração externa
O pipeline deve usar YAML para metadados da obra, público, transformação prometida, tom de voz e regras editoriais.

### FR-04 Metadados controlados por código
Título, autor, rótulo temporal da obra e caminho da fonte devem vir da configuração, não da IA.

### FR-05 Geração do briefing
O Agente Editorial deve gerar briefing com:
- metadados;
- público-alvo;
- transformação prometida;
- cinco ideias centrais;
- tom de voz;
- justificativa do tom.

### FR-06 Mapa estruturado de ideias
Antes da escrita do microbook, o sistema deve gerar uma camada intermediária de conhecimento editorial contendo ideias centrais, origem aproximada no material e temas.

### FR-07 Geração do microbook
O Agente Editorial deve gerar microbook em Markdown com 800 a 1.000 palavras.

### FR-08 Aderência ao briefing
O microbook deve desenvolver as cinco ideias centrais e refletir público e tom definidos.

### FR-09 Fidelidade ao material-fonte
O microbook não deve apresentar como fato afirmações sem sustentação na obra.

### FR-10 Revisão explícita
O Agente de Revisão deve avaliar briefing, microbook e aderência à fonte.

### FR-11 Registro da revisão
A revisão deve registrar:
- itens mantidos;
- itens modificados;
- itens rejeitados;
- justificativas.

### FR-12 Validação estrutural
O código deve validar presença de campos obrigatórios nas saídas estruturadas.

### FR-13 Validação de contagem de palavras
O código deve medir a contagem de palavras do microbook e reportar divergência do intervalo esperado.

### FR-14 Geração dos roteiros
O Agente de Distribuição deve gerar três roteiros distintos:
- educacional;
- contrário ou provocativo;
- UGC.

### FR-15 Estrutura obrigatória dos roteiros
Cada roteiro deve conter:
- gancho;
- desenvolvimento;
- sugestão visual;
- CTA;
- plataforma prioritária;
- justificativa da plataforma.

### FR-16 Fidelidade na adaptação
Os roteiros devem preservar a ideia central do microbook sem copiar literalmente sua redação.

### FR-17 Operação editorial
O projeto deve produzir resposta objetiva para o cenário de atraso e risco de informação inventada.

### FR-18 Registro do uso de IA
O projeto deve documentar ferramentas, atividades, prompts importantes, exemplo de saída modificada ou rejeitada e estratégia de verificação.

### FR-19 Renderização Markdown
As saídas finais devem ser salvas em arquivos Markdown legíveis.

## 6. Requisitos Não Funcionais

### NFR-01 Clareza
O código deve priorizar nomes claros, módulos curtos e fluxo legível.

### NFR-02 Modularidade
A troca de provedor de LLM deve ocorrer sem alteração da lógica de negócio principal.

### NFR-03 Proporcionalidade
A arquitetura deve permanecer enxuta e adequada ao escopo de teste.

### NFR-04 Testabilidade
Partes determinísticas críticas devem possuir testes com `pytest`.

### NFR-05 Transparência
Limitações, divergências e dependências externas devem ser documentadas.

## 7. Restrições
- Linguagem principal: Python.
- Modelos tipados: Pydantic ou equivalente.
- Configuração: YAML ou JSON.
- Saídas: Markdown.
- Não inventar conteúdo bibliográfico sem sinalizar a origem.
- Não usar IA para metadados fixos.

## 8. Casos de Erro
- Arquivo-fonte ausente.
- PDF sem texto extraível.
- YAML inválido.
- Resposta do LLM fora do formato solicitado.
- Microbook fora do intervalo de palavras.
- Roteiros com campos obrigatórios ausentes.
- Falha de autenticação no provedor de LLM.

## 9. Comportamento Esperado
- O pipeline deve interromper quando faltar a fonte ou a configuração.
- O pipeline deve persistir relatórios de revisão mesmo quando houver ressalvas.
- O pipeline deve apontar limites reais em vez de mascará-los.

## 10. Ambiguidades Resolvidas
- **Ano de publicação de obra clássica**: será tratado como rótulo temporal confiável, com nota de proveniência, caso a edição do PDF não exponha metadados editoriais suficientes.
- **Google Docs**: a automação de publicação não faz parte do escopo local; o projeto entrega o texto pronto para colagem, com limitação documentada.
- **RAG**: não será adotado por padrão, pois o PDF fornecido possui 37 páginas e pode ser processado diretamente de forma confiável.
- **Camada intermediária editorial**: a solução usa um mapa estruturado de ideias em JSON antes da geração do microbook, não como mecanismo de recuperação estilo RAG, mas como base editorial rastreável.
