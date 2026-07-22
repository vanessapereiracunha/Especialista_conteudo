# Critérios de Aceitação

## AC-01 Fonte disponível
**Dado** um caminho válido em `config/editorial.yaml`  
**Quando** a pipeline iniciar  
**Então** o arquivo-fonte deve ser carregado com sucesso.

## AC-02 Erro de fonte ausente
**Dado** um caminho inexistente  
**Quando** a pipeline iniciar  
**Então** o sistema deve encerrar com mensagem clara orientando o uso de `data/source/`.

## AC-03 Configuração tipada
**Dado** um YAML válido  
**Quando** a configuração for carregada  
**Então** os campos obrigatórios devem ser validados por modelo tipado.

## AC-04 Briefing completo
**Dado** uma execução bem-sucedida do agente editorial  
**Quando** `output/editorial.md` for gerado  
**Então** o briefing deve conter todos os campos obrigatórios.

## AC-05 Mapa editorial estruturado
**Dado** uma execução bem-sucedida do mapeador de ideias  
**Quando** `output/editorial_ideas.json` for gerado  
**Então** o arquivo deve conter entre 5 e 8 ideias, cada uma com origem e temas.

## AC-06 Microbook no intervalo
**Dado** um microbook gerado  
**Quando** a contagem de palavras for calculada  
**Então** o valor deve ficar entre 800 e 1.000 palavras.

## AC-07 Fidelidade explícita
**Dado** o relatório de revisão  
**Quando** ele for salvo  
**Então** deve haver avaliação de aderência à fonte e sinalização de possíveis extrapolações.

## AC-08 Revisão registrada
**Dado** a etapa de revisão  
**Quando** `output/review.md` for criado  
**Então** o arquivo deve incluir exemplo mantido, modificado e rejeitado.

## AC-09 Roteiros completos
**Dado** a etapa de distribuição  
**Quando** `output/distribution.md` for gerado  
**Então** cada um dos três roteiros deve conter gancho, desenvolvimento, cena, CTA, plataforma e justificativa.

## AC-10 Diferença de abordagens
**Dado** os três roteiros gerados  
**Quando** forem comparados  
**Então** eles devem apresentar abordagens editorialmente distintas.

## AC-11 Operação editorial objetiva
**Dado** o cenário de atraso e risco editorial  
**Quando** `output/operacao_editorial.md` for produzido  
**Então** o texto deve cobrir priorização, paralelismo, comunicação e melhoria de processo.

## AC-12 Transparência de IA
**Dado** `output/ai_usage.md`  
**Quando** o arquivo for revisado  
**Então** ele deve listar ferramentas, atividades, prompts-chave, exemplo de resposta modificada ou rejeitada e método de verificação.

## AC-13 Troca de provedor sem refatoração do domínio
**Dado** um novo provedor compatível  
**Quando** `llm_client.py` for ajustado  
**Então** agentes e pipeline não devem precisar de mudanças estruturais.
