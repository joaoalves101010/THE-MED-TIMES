# Escopo da exportação pública

Esta entrega preserva o site de leitura e as fontes necessárias para reconstruí-lo, sem transferir a infraestrutura privada de publicação.

## Preservado sem alteração editorial

Todos os 327 arquivos HTML do site, CSS/JavaScript de leitura e históricos, fontes tipográficas, licenças, marca, fotografias, diagramas e as quatro miniaturas atualmente utilizadas. Os dados de matérias, datas, fontes e históricos não foram reescritos. Os recursos públicos também estão em `src/assets/` para permitir um build limpo.

## Exclusões intencionais

- Metadados de plataforma, histórico `.git`, diretórios de ambiente e caches.
- `dist/RELEASE_MANIFEST.json`, `dist/release-evidence.json`, `dist/release-provenance/` e `maintenance-provenance/`: registros internos de publicação/proveniência, sem função na leitura do site.
- `src/editions/004/EDITORIAL_REVIEW.json`: registro bruto de revisão, não conteúdo do jornal.
- `proofs/`, `masthead-horizontal-proof.png`, `DAILY_TEST_RESULTS.json`, `UI_READING_QA.md` e `ARTWORK_METADATA.json`: artefatos de trabalho/QA e metadados não necessários à hospedagem.
- Os scripts privados de manutenção, promoção e publicação, e os geradores antigos isolados das edições 001/002. Seus resultados históricos necessários permanecem em `src/editions/` e são preservados pelo gerador atual.
- Duas variantes antigas e não referenciadas da miniatura 004 (`edition-004-adeb4273104d0980.png` e `edition-004-c95c4271333e8b33.png`), tanto em fonte quanto em saída. A miniatura atual e as três históricas continuam intactas.

## Ajustes de portabilidade

- `edition.json`: identidade pública `the-med-times` e modo `manual-snapshot`; número, datas, seleção e histórico mantidos.
- `src/editions/002/photos.json`: removidos somente os dois campos `localPath` específicos da máquina; créditos, fonte, licença e direitos preservados.
- `build.py`: cópia explícita dos recursos-fonte para reconstrução limpa.
- `archive_previews.py`: dependências gráficas carregadas somente quando uma prova nova precisa ser gerada; o reuso da prova atual exige correspondência de hashes de HTML, CSS, imagens/fontes e PNG.
- Política v2 e testes preservados com utilitários editoriais portáteis. A preparação foi reduzida ao modelo pendente e à validação das entradas; não há publicador ou acesso à infraestrutura original.
- Documentação nova e validação pública independente em Node; nenhum segredo, usuário de infraestrutura ou chave de exemplo foi criado.

Essas exceções não mudam os fatos das matérias, a aparência atual ou os links do arquivo. O acesso e a publicação do ambiente original não foram modificados.
