# Publicação na Vercel

Domínio informado: [https://themedtimes.vercel.app/](https://themedtimes.vercel.app/). A configuração da conta, projetos e proteção de acesso é do proprietário. Este repositório não cria contas, chaves, serviços pagos, domínios ou cron jobs.

## Configuração

Importe `joaoalves101010/THE-MED-TIMES` usando a raiz do repositório. O `vercel.json` define:

| Opção | Valor |
| --- | --- |
| Framework | Other (`null`) |
| Node | 24.x |
| Instalação | comando Node sem pacotes npm |
| Build | `npm run build` |
| Saída | `dist` |
| Variáveis de ambiente | nenhuma |

O build valida o artefato pronto, sem rodar Python, Pillow ou PyMuPDF. Não usar Next.js, não publicar a raiz inteira e não aplicar rewrite universal para `index.html`: existem rotas HTML reais e `404.html`.

## Verificação após cada commit

Aguardar o resultado do deploy, quando houver estado/check disponível, e confirmar o domínio público. Conferir edição **005**, data **2026-10-26**, capa, seis cadernos com 16 matérias, uma matéria atual, busca de 96 resultados, arquivo completo, fontes locais e 404. Conferir também navegação móvel, foco, Busca/Cadernos e ausência de cortes.

Se a página ainda exibir a edição anterior, o commit no GitHub não deve ser anunciado como edição pública concluída. Investigar a conexão/deploy com as permissões existentes. Não criar outro projeto ou conta como contorno.

## Mudanças locais

Reconstruir e testar: `python3 build.py`, `npm run test:python`, inspeção editorial/visual e `npm run snapshot:hashes` somente após aprovação. Executar novamente `npm test` e versionar fonte, `dist/` e hashes juntos.

Referências oficiais: [configuração de build](https://vercel.com/docs/builds/configure-a-build), [vercel.json](https://vercel.com/docs/project-configuration/vercel-json), [Node.js](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions). A conexão Git pode publicar commits; ela não pesquisa notícias nem substitui a preparação editorial.
