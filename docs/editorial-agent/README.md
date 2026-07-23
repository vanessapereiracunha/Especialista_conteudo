# README — Agente Editorial

## Problema que resolve
Transforma uma obra-fonte em um briefing editorial utilizável e em um microbook consistente com público, tom e foco editorial.

## Entradas
- metadados fixos da obra;
- configuração editorial em YAML;
- mapa estruturado de ideias com origem e temas;
- texto extraído do material-fonte.

## Saídas
- briefing editorial;
- microbook em Markdown;
- estrutura pronta para revisão.

## Como o briefing orienta a geração
O briefing fixa público, transformação, cinco ideias centrais e tom de voz. O microbook é gerado a partir dessas diretrizes e do mapa estruturado de ideias, não por improviso livre do modelo.

## Como o público-alvo influencia o conteúdo
O público-alvo orienta nível de abstração, vocabulário, exemplos e promessa editorial. Aqui, a escrita prioriza aplicação estratégica para profissionais de conteúdo, marketing, liderança e operação.

## Como o tom de voz influencia a geração
O tom escolhido é claro, estratégico, pragmático e acessível. Isso evita uma saída excessivamente acadêmica ou grandiloquente.

## Como a fidelidade ao material original é verificada
- o sistema extrai antes um mapa estruturado de ideias com origem e temas;
- texto da fonte entra no prompt;
- metadados fixos e informações estruturais são controlados pelo código, em vez de serem inventados ou inferidos pelo modelo;
- existe uma etapa posterior de revisão dedicada a detectar extrapolações.

## Papel do mapa estruturado de ideias
O mapa estruturado funciona como uma representação intermediária entre a fonte original e a geração editorial. Ele permite inspecionar as ideias selecionadas e suas referências antes que sejam transformadas em conteúdo.

## Como a revisão melhora a fidelidade
A revisão posterior compara afirmações do conteúdo com o mapa estruturado de ideias e suas evidências textuais, classificando possíveis extrapolações e indicando quais trechos precisam de revisão editorial.

## Limitações
- a fidelidade ainda depende da qualidade da extração do PDF;
- sem credenciais de LLM não há geração ao vivo;
- a avaliação semântica continua exigindo julgamento editorial humano.

## Como a IA é utilizada
A IA é usada para sintetizar o material-fonte em duas etapas: primeiro em um mapa estruturado de ideias; depois em briefing e microbook, respeitando instruções de forma, tom, público e limites editoriais.

## Partes controladas pelo código
- leitura da configuração;
- leitura da fonte;
- validação estrutural;
- contagem de palavras;
- persistência em Markdown.

## Partes geradas pelo modelo
- seleção das cinco ideias centrais;
- justificativa do tom;
- redação do microbook.
