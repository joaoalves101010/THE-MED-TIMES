# Publicação manual na Vercel

## Estado deste repositório

O site está público em [themedtimes.vercel.app](https://themedtimes.vercel.app/). O deploy inicial foi concluído e sua primeira página conferida contra o artefato versionado. A conta e a conexão Git da Vercel são do proprietário. Este repositório não cria contas, serviços pagos, chaves, cron jobs nem altera o acesso do ambiente privado original.

## Importar

1. Na Vercel, crie um projeto importando `joaoalves101010/THE-MED-TIMES`.
2. Use a raiz do repositório como **Root Directory** (`.` / campo vazio).
3. Confirme as configurações abaixo. Elas já constam no `vercel.json`.
4. Para reproduzir a instalação em sua conta, publique e confira as rotas abaixo. O endereço atual já foi informado e verificado.

| Configuração | Valor |
| --- | --- |
| Framework Preset | **Other** (`framework: null`) |
| Node.js | **24.x** |
| Install Command | `node -e "console.log('Site estatico: sem dependencias npm')"` |
| Build Command | `npm run build` |
| Output Directory | **dist** |
| Variáveis de ambiente | Nenhuma |

O comando chamado “build” apenas verifica os arquivos já versionados: hashes, 96 matérias, seis cadernos, fontes locais, links e ausência de registros privados no diretório público. **Ele não executa o gerador Python.** Assim, a Vercel não precisa de Pillow, PyMuPDF, pacotes pip ou ferramentas gráficas.

Não escolha Next.js, não configure a raiz como `dist`, não publique a raiz do repositório inteira e não adicione um rewrite universal para `index.html`: o jornal tem páginas HTML reais e arquivos históricos independentes. O `404.html` já está em `dist/`.

## Conferir depois do deploy

- `/`: edição 004, data original, capa branca e nove chamadas.
- `/editorias/pesquisa/` e os demais cinco cadernos: 16 matérias cada.
- Uma rota `/edicao-004/artigos/.../`: texto, fonte, data e leituras relacionadas.
- `/?q=`: 96 resultados; testar busca, filtros e estado sem resultado.
- `/edicao/`: quatro edições, miniaturas e links funcionais.
- `/edicoes/001/`, `/edicoes/002/` e `/edicoes/003/`: datas e aparências históricas intactas.
- Uma rota inexistente: página de erro, não um falso resultado da primeira página.
- Em tela pequena: Cadernos, Buscar, foco, fechamento por Escape e ausência de cortes.

## Quando houver mudanças

Após edição autorizada: reconstruir localmente, executar as verificações completas, revisar em navegador e só então atualizar `public-dist-sha256.json` com `npm run snapshot:hashes`. Rode novamente `npm test` e `npm run test:python`; versione juntos fonte, `dist/` e hashes.

O envio recorrente de próximas edições ao GitHub foi autorizado. O fluxo editorial em consolidação separa a preparação às 06:30 da publicação a partir de 08:00, no horário de São Paulo. A etapa de preparação não pode atualizar a branch pública; a publicação usa o artefato validado, verifica conflitos e não força a referência Git.

Depois de cada commit, conferir o status do deploy e a edição no domínio público. Se ainda estiver disponível a edição anterior, não anunciar a nova como publicada. **A conexão Git da Vercel não pesquisa notícias nem faz curadoria:** ela publica os commits recebidos. O deploy inicial foi verificado; isso não prova, antecipadamente, que a recorrência diária completa já foi executada. Nenhuma credencial foi adicionada ao repositório.

## Referências oficiais

Configurações verificadas na documentação oficial: [build, saída e framework Other](https://vercel.com/docs/builds/configure-a-build), [vercel.json](https://vercel.com/docs/project-configuration/vercel-json) e [versões Node.js](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions). As opções da plataforma podem mudar; o deploy real precisa ser conferido na conta do proprietário.
