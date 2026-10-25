# Contexto do projeto

## Identidade e experiência

THE MED TIMES é um jornal editorial em português para estudantes de medicina e leitores interessados em ciência. A identidade combina marca vetorial, Nimbus Roman/Nimbus Sans locais e composição de jornal. A interface atual tem papel branco na capa e nos seis cadernos; o arquivo mantém as aparências de suas respectivas edições.

As seis editorias são Pesquisa, Clínica, Saúde pública, Formação, Inovação e Instituições. A edição 004 reúne 96 matérias, 16 por editoria. A capa apresenta nove chamadas selecionadas, não todos os conteúdos. Busca, filtros, navegação acessível, rótulos de evidência, datas de fonte e leituras relacionadas já estão implementados.

## Estado editorial congelado

- **001 — 24.10.2026:** edição inaugural, seis matérias, ilustrações de IA identificadas.
- **002 — 24.10.2026:** atualização da noite, sete matérias e fotografias documentais creditadas.
- **003 — 24.10.2026:** edição ampliada, 96 matérias; HTML/CSS/JS congelados.
- **004 — 25.10.2026:** edição diária atualmente aberta na raiz, com 96 matérias.

Não trocar datas para simular atualidade. Não interpretar esta exportação ou o sucesso dos testes como nova checagem factual. Fontes externas podem mudar; a precisão editorial de uma futura edição requer consulta real às fontes e revisão dos limites da evidência.

## Regras de continuidade

1. Preservar textos, datas e URLs das edições já publicadas. Para uma edição futura, criar uma nova pasta/namespace e arquivar a anterior antes de torná-la histórica.
2. Manter recursos históricos imutáveis. Uma imagem ou diagrama alterado precisa de um nome novo, sem sobrescrever arquivos usados pelo arquivo.
3. Preservar a diferença entre notícia, guia, programa institucional e referência sem data.
4. Não apresentar protótipos como tratamentos disponíveis, associação como causalidade, metas como resultados ou programas como inscrições abertas sem comprovação.
5. Manter fontes primárias, autoria, licença e ressalvas de fotografias/diagramas. Não remover as licenças das fontes tipográficas.
6. Não afirmar revisão médica independente. O site informa assistência de IA e finalidade educativa, sem substituição de avaliação profissional.
7. Aplicar a política v2 de renovação integral às próximas edições, sem alegar retrospectivamente que a edição atual já passou nela.

## Arquitetura e limites

HTML/CSS/JavaScript estáticos, sem banco de dados ou dependências npm. O gerador Python recebe dados JSON explícitos e não usa a data atual para trocar a data editorial. A pesquisa de matérias não faz parte do build.

`public-dist-sha256.json` registra apenas arquivos públicos, hashes e identidade portátil `the-med-times`. Não é uma assinatura de autoridade, uma aprovação editorial ou evidência de deploy. Os testes de comportamento usam o JavaScript real em um DOM simulado; não substituem inspeção em navegadores, dispositivos e no domínio de produção.

A publicação programada existente continua somente no ambiente privado original. Este GitHub é uma entrega inicial independente: a Vercel será configurada pelo proprietário. Não existem sincronização, credenciais, tarefas agendadas ou integração de publicação no repositório. Antes de automatizar, é necessário definir explicitamente destino público, autorização, revisão, gatilhos, registro de falhas e recuperação.
