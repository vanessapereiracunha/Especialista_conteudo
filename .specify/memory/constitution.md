# Constitution

## Objetivo
Construir uma pipeline editorial assistida por IA, simples e rastreável, capaz de transformar uma obra-fonte em briefing editorial, microbook, revisão crítica e roteiros de distribuição sem ultrapassar o escopo de um teste técnico.

O uso de SDD/Spec Kit serve para estruturar requisitos e critérios de aceitação. O trabalho principal do projeto está na implementação da pipeline, nos contratos de saída, nas validações, na rastreabilidade e na revisão crítica.

## Princípios

1. **Simplicidade antes de complexidade**
   A solução deve resolver o teste com o menor número de abstrações necessário. Toda camada, arquivo ou validação precisa justificar sua existência.

2. **Fidelidade editorial ao material-fonte**
   O conteúdo gerado deve permanecer ancorado na obra fornecida. Quando houver incerteza bibliográfica, a saída deve registrar a limitação em vez de inventar precisão.

3. **Separação entre determinístico e generativo**
   Metadados fixos, estrutura de arquivos, renderização Markdown, validações, contagem de palavras e persistência pertencem ao código. Geração editorial, adaptação de linguagem e sugestões criativas pertencem ao modelo.

4. **IA como colaboradora, não como fonte de verdade**
   Toda saída gerada por IA deve passar por uma etapa explícita de revisão. O sistema deve facilitar detectar extrapolações, lacunas e informações não sustentadas.

5. **Qualidade editorial acima de volume**
   O objetivo não é maximizar quantidade de texto, e sim produzir conteúdo claro, útil, coerente e adequado ao público definido.

6. **Rastreabilidade proporcional**
   Requisitos, especificação, plano, tarefas, implementação e validação devem se conectar de forma clara, mas sem documentação ornamental.

7. **Modularidade pragmática**
   A arquitetura deve permitir trocar provedor de LLM e adaptar o pipeline para outro livro sem refatorações amplas, evitando padrões excessivos para um teste curto.

8. **Falhas explícitas e recuperáveis**
   Ausência de arquivo-fonte, configuração inválida, campos obrigatórios ausentes e problemas de parsing devem gerar erros claros para o operador.

9. **Testabilidade realista**
   Devem existir testes para partes determinísticas e validações críticas. Não é necessário testar comportamento probabilístico do LLM como se fosse determinístico.

10. **Transparência no uso de IA**
    O projeto deve registrar onde a IA foi usada, quais prompts foram importantes, o que foi aceito, o que foi modificado e o que foi rejeitado.

11. **Proporcionalidade ao escopo**
    Não implementar RAG, banco vetorial, filas, APIs web ou orquestração distribuída sem necessidade demonstrável pelo tamanho do material-fonte ou pelos critérios do teste.

12. **Comunicação clara**
    Decisões técnicas, limitações e divergências entre especificação e implementação devem ser registradas em linguagem simples, objetiva e verificável.
