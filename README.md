# THE MED TIMES

Jornal estático em português sobre medicina, ciência e descobertas.

**Edição atual: 006, de 2026-10-28.** Este repositório contém o código-fonte, o site pronto em `dist/`, recursos locais, fontes/licenças e todo o histórico editorial disponível.

- Primeira página branca, seis cadernos com composições próprias e nove chamadas de capa.
- 96 matérias na edição atual: 16 por editoria; busca local, filtros, navegação móvel e leituras relacionadas.
- Textos, datas, fontes, imagens e créditos históricos preservados; publicar um commit não altera as datas das notícias.

## Publicação

O envio recorrente de próximas edições para este repositório foi autorizado pelo proprietário. Cada envio continua condicionado à pesquisa, renovação integral e validação editorial, à integridade do artefato e à ausência de conflitos com alterações feitas no GitHub. O repositório não contém credenciais nem instala um agendador por conta própria.

Endereço público informado pelo proprietário: [https://themedtimes.vercel.app/](https://themedtimes.vercel.app/). A publicação de um commit pode acionar a conexão Git da Vercel, se configurada na conta. **Sucesso no GitHub não comprova sucesso na Vercel:** o domínio público precisa ser verificado após cada publicação. A recorrência completa não é garantida apenas por este código.

Vercel: **Other**, raiz do repositório, saída **dist**, `npm run build`. O build da hospedagem valida o artefato pronto com Node, sem Python ou dependências npm. Consulte [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md).

## Uso local

Node 24 e Python 3.11+; não é necessário `npm install`.

```sh
npm test
npm run test:python
python3 -m http.server 8000 --directory dist
```

Para reconstruir a edição existente: `python3 build.py`. Recursos imutáveis estão em `src/assets/`; miniaturas existentes são reutilizadas somente com hashes de HTML, CSS, recursos e PNG correspondentes. Miniaturas novas exigem Pillow e PyMuPDF, opcionais em `requirements-build.txt`. Miniaturas estáticas não substituem testes visuais em navegador.

`src/editions/` guarda dados e páginas históricas; `src/styles.css` e `src/app.js` são a interface atual; `src/historical-ui/` preserva o código antigo. O gerador utiliza `build.py`, `templates.py`, `press_renderer.py` e `compositions.py`. Os testes e `public-dist-sha256.json` protegem o artefato público.

Veja [contexto](CONTEXTO_PROJETO.md), [política diária](DAILY_PUBLISHING.md), [escopo da exportação](EXPORTACAO_PUBLICA.md) e [direitos e licenças](LICENSE_NOTICE.md).
