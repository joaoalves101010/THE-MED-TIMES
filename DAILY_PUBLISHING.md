# Política diária — v2

Objetivo: nova edição às **08:00 em America/Sao_Paulo**, somente após pesquisa e validação. A preparação anterior ao horário não autoriza alteração da referência pública do GitHub. O envio recorrente foi autorizado para este repositório, mas sua execução e o deploy da Vercel precisam ser confirmados por edição.

## 96 pautas novas

Exigir 96 pautas globalmente novas, 16 por editoria, com nove chamadas escolhidas. Rejeitar reutilização de IDs, fontes, títulos e corpos da edição anterior, incluindo aliases e URLs de rastreamento. Exigir comparação semântica com todas as pautas anteriores/candidatas e revisão de arquivos relevantes. A mesma pauta reescrita não é novidade.

`renewal_policy.py` contém essas verificações; não entende sozinho todas as equivalências semânticas. Registrar apenas revisões e consultas realmente realizadas. A política vale prospectivamente: não reescreve nem certifica retroativamente os arquivos antigos.

## Modelo pendente e validação

Organizar fora de `dist/` seis JSON com 16 matérias cada e `home-selection.json` com nove IDs. O comando `python3 prepare_editorial.py template --help` explica como criar um modelo sem aprovação. Preencher com pesquisa real e executar `python3 prepare_editorial.py validate --help` para conferir entradas. O programa usa os dados-fonte da edição atual como comparação e não publica, não pesquisa fontes e não faz revisão médica independente.

Não incluir identidades/observações privadas de revisão no Git público. Datas, corte, fonte HTTPS, hashes, direitos, rotulagem, composições e checagens precisam ser consistentes. Não inventar prazos ou datas para cumprir o horário.

## Publicação segura

Usar exatamente o artefato validado, preservar todas as edições e recursos históricos, verificar conflitos com o HEAD público atual e nunca forçar atualização da branch. Um candidato de teste ou sintético jamais deve ser publicado. Se qualquer etapa falhar, manter a edição anterior com sua data original.

Depois do commit, verificar o deploy no domínio público. GitHub atualizado e Vercel atualizada são resultados distintos. O código público não contém os registros privados de revisão nem as credenciais do processo editorial.
