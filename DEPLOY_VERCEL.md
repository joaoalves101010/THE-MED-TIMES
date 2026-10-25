# Publicação manual na Vercel

## Estado deste repositório

O site está pronto em `dist/`; o domínio público e o projeto da Vercel ainda devem ser definidos pelo proprietário. Esta exportação não cria projeto, domínio, cron, webhook, segredo ou deploy na Vercel e não altera o acesso do ambiente privado original.

## Importar

1. Na Vercel, crie um projeto importando `joaoalves101010/THE-MED-TIMES`.
2. Use a raiz do repositório como **Root Directory** (`.` / campo vazio).
3. Confirme as configurações abaixo. Elas já constam no `vercel.json`.
4. Publique pela sua conta; depois confira as rotas e compartilhe o endereço público para a validação de produção.

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

A conexão Git da Vercel poderá publicar futuros commits se essa opção estiver habilitada na conta. **Isso não pesquisa notícias, não produz edições e não sincroniza automaticamente o ambiente privado.** A renovação diária depende de uma integração editorial futura, ainda não configurada aqui.

## Referências oficiais

Configurações verificadas na documentação oficial: [build, saída e framework Other](https://vercel.com/docs/builds/configure-a-build), [vercel.json](https://vercel.com/docs/project-configuration/vercel-json) e [versões Node.js](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions). As opções da plataforma podem mudar; o deploy real precisa ser conferido na conta do proprietário.
