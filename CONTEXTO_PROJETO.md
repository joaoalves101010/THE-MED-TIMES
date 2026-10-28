# Contexto do projeto

THE MED TIMES é um jornal editorial em português para estudantes de medicina e leitores de ciência. A identidade combina marca vetorial, fontes Nimbus locais e composição de jornal. A edição atual tem papel branco na capa e nos seis cadernos; os arquivos mantêm suas aparências históricas.

## Edições disponíveis

- **001 — 2026-10-24:** Edição inaugural; 6 matérias; arquivo preservado.
- **002 — 2026-10-24:** Atualização da noite; 7 matérias; arquivo preservado.
- **003 — 2026-10-24:** Edição ampliada; 96 matérias; arquivo preservado.
- **004 — 2026-10-25:** Edição diária; 96 matérias; arquivo preservado.
- **005 — 2026-10-26:** Edição diária; 96 matérias; arquivo preservado.
- **006 — 2026-10-28:** edição atual; 96 matérias, 16 por editoria.

`/edicao/` reúne as edições. A edição 006 é a atual, acessível na raiz: não se cria um arquivo histórico duplicado antes de sua substituição.

## Continuidade editorial

Preservar fatos, datas, fontes, direitos e bytes dos recursos históricos. Mudanças de imagem/diagrama exigem novo nome, nunca sobrescrita de um recurso utilizado pelo arquivo. Não trocar datas para simular atualidade. Manter a distinção entre notícia, guia, programa institucional e referência sem data.

Não apresentar associação como causalidade, metas como resultados, protótipos como tratamentos disponíveis ou programas como inscrições abertas sem comprovação. Manter fontes primárias, créditos, licenças, ressalvas e rótulos de IA. O conteúdo é educativo, não substitui avaliação individual e não afirma revisão médica independente.

## Arquitetura e limites

HTML, CSS e JavaScript estáticos, sem banco de dados. O build recebe JSON explícito e não pesquisa notícias nem deduz a data da edição pelo relógio atual. Cada nova edição exige 96 pautas novas conforme a política v2, mais revisão semântica e consulta real às fontes.

Os hashes públicos identificam bytes, não são uma assinatura de autoridade nem comprovação factual. Os testes JS usam o código real em um DOM simulado; testes estáticos e de contrato não substituem inspeção em navegador e no domínio público.

Alterações manuais no GitHub não devem ser sobrescritas pelo fluxo editorial. Conflitos em arquivos administrados devem ser resolvidos antes de uma próxima publicação; arquivos não relacionados devem ser preservados.
