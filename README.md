# THE MED TIMES

Jornal digital estático, em português, sobre medicina, ciência e descobertas.

**Este repositório é um snapshot completo e portátil da edição 004, de 25 de outubro de 2026.** Contém o código-fonte, o site pronto em `dist/`, os recursos locais e as edições anteriores. Nenhum deploy na Vercel é realizado por este repositório sozinho.

## O que está preservado

- Primeira página e seis cadernos com papel branco e composições próprias.
- 96 matérias na edição atual: 16 por editoria e nove chamadas na capa.
- Busca local por texto, editoria e tipo; navegação móvel e retorno à origem da leitura.
- Fontes, datas, textos, fotografias, diagramas e créditos existentes, sem revisão factual nova nesta exportação.
- Edições 001 e 002 e snapshot histórico da edição 003. A edição 004 é a edição atual: `/edicao/` reúne as quatro, sem inventar um arquivo duplicado `/edicoes/004/`.

## Publicar na Vercel

Importe este repositório na sua conta e use as configurações de [`DEPLOY_VERCEL.md`](DEPLOY_VERCEL.md): **Framework Other, raiz do repositório, saída `dist`**. O `vercel.json` valida o artefato já pronto com Node e não executa Python, não instala pacotes npm e não depende de serviços privados.

**Não há renovação automática de conteúdo no GitHub/Vercel configurada.** A publicação programada do ambiente privado original não está sincronizada com este snapshot. Importar o repositório na Vercel não cria essa integração. O texto editorial existente sobre publicação programada foi preservado; ele não comprova a configuração de uma agenda nesta hospedagem.

## Executar e verificar localmente

Requisitos: Node 24 e Python 3.11+ (testado com Python 3.12). Não é necessário `npm install`.

```sh
npm test
npm run test:python
python3 -m http.server 8000 --directory dist
```

Abra `http://localhost:8000`. Sirva `dist/`, não a raiz do repositório. A busca usa JavaScript no navegador; não há backend, conta, pagamento ou rastreamento.

### Reconstruir a edição existente

```sh
python3 build.py
npm test
npm run test:python
```

`src/assets/` permite reconstruir inclusive depois de remover `dist/`. As miniaturas já aprovadas são reutilizadas somente quando os hashes do HTML, CSS, recursos e PNG correspondem. O snapshot pode ser reconstruído sem bibliotecas Python externas.

Para gerar miniaturas de uma edição ou composição **nova**, instale em um ambiente virtual as dependências opcionais de `requirements-build.txt` (Pillow e PyMuPDF). Miniaturas são provas estáticas aproximadas, não capturas de navegador nem validação visual de responsividade.

## Organização

| Caminho | Conteúdo |
| --- | --- |
| `dist/` | Site público pronto para hospedagem estática |
| `src/editions/` | Dados editoriais e páginas históricas imutáveis |
| `src/assets/` | Fontes, licenças, marca, diagramas e fotografias locais |
| `src/archive-previews/` | Miniaturas utilizadas e metadados de integridade |
| `src/styles.css`, `src/app.js` | Interface da edição atual |
| `src/historical-ui/` | CSS/JS históricos preservados |
| `build.py`, `templates.py`, `press_renderer.py`, `compositions.py` | Geração das páginas e composições |
| `verify.py`, `test_*.py`, `test_reading_ui.js` | Verificações estruturais, editoriais e comportamentais |
| `scripts/`, `public-dist-sha256.json` | Validação portátil do artefato público |
| `prepare_editorial.py`, `renewal_policy.py` | Modelo de revisão e validação de entradas de futuras edições |

Leia [`CONTEXTO_PROJETO.md`](CONTEXTO_PROJETO.md), [`DAILY_PUBLISHING.md`](DAILY_PUBLISHING.md), [`EXPORTACAO_PUBLICA.md`](EXPORTACAO_PUBLICA.md) e [`LICENSE_NOTICE.md`](LICENSE_NOTICE.md) antes de modificar ou publicar uma nova edição.
