# Política editorial diária — v2

## Intenção, não automação instalada

O objetivo editorial é uma nova edição às **08:00 em America/Sao_Paulo**, somente depois de pesquisa e validação. Este repositório não possui scheduler, GitHub Actions de publicação, cron da Vercel ou sincronização com o ambiente privado original. Sem uma nova edição aprovada e um commit/deploy correspondente, o público continuará vendo este snapshot, com sua data original.

A edição 004 foi preservada como publicada. A política v2 orienta as próximas edições; não significa que este acervo histórico foi reescrito ou aprovado retrospectivamente pelas regras de novidade.

## Renovação integral

Cada edição futura deve trazer **96 pautas novas**, 16 por editoria, com nove chamadas de capa escolhidas explicitamente. Não bastam uma nova data, novos títulos ou a substituição de algumas notícias.

`renewal_policy.py` exige comparação com a edição imediatamente anterior e revisão dos arquivos relevantes. Rejeita IDs, URLs de fonte, títulos e corpos repetidos, inclusive normalizações e parâmetros de rastreamento. Exige também revisão semântica de cada pauta em relação a todas as pautas anteriores e candidatas, explicação da diferença e chaves temáticas únicas.

Essas verificações determinísticas **não entendem sozinhas todas as equivalências semânticas**. Mudar URL, nome de instituição ou redação não transforma o mesmo evento em pauta nova. O registro editorial deve documentar a comparação de verdade, nunca preencher campos de aprovação automaticamente.

## Preparar um registro de revisão

Organize uma pasta externa ao diretório público com os seis arquivos `pesquisa.json`, `clinica.json`, `saude-publica.json`, `formacao.json`, `inovacao.json`, `instituicoes.json`, cada um com 16 matérias completas, e `home-selection.json` com nove IDs. Preserve o formato das fontes em `src/editions/004/`.

O comando abaixo mostra a interface; substitua as variáveis por dados reais. Não contém aprovação pronta:

```sh
python3 prepare_editorial.py template \
  --input "$PASTA_CANDIDATA" --date "$DATA_LOCAL" \
  --cutoff "$CORTE_ISO_COM_FUSO" --output "$REVISAO_PRIVADA"
```

O modelo começa com campos pendentes, sem revisor, sem horários e sem aprovações. **Mantenha o registro preenchido fora de `dist/` e fora do Git público** quando contiver identidade ou notas privadas. `prepare_editorial.py` não publica e não faz pesquisas de fontes por conta própria.

Depois da pesquisa real e revisão:

```sh
python3 prepare_editorial.py validate \
  --edition "$NOVA_EDICAO" --date "$DATA_LOCAL" \
  --input "$PASTA_CANDIDATA" --review "$REVISAO_PRIVADA"
```

A validação usa os dados-fonte da edição atual como anterior. Exige data local real, corte e revisão no dia adequado, hashes de conteúdo, fonte HTTPS, 96 registros completos, checagem das fontes, revisão de direitos, rotulagem editorial, composições e fonte móvel. Rejeita datas de publicação futuras, textos provisórios, checagens vencidas e linguagem relativa de data usada como novidade em notícia antiga. A saída aprovada significa somente **entrada editorial válida**, não publicação, verdade garantida ou revisão médica independente.

## Antes de publicar

Arquivar a edição anterior, montar a nova configuração e namespace, revisar direitos de novos recursos e executar build, testes, inspeção visual e revisão de fontes. Atualizar os hashes públicos somente após aprovação. Não contornar falhas de novidade ou fatos para cumprir horário. Se qualquer etapa falhar, preservar a edição anterior e não alterar sua data.

A integração entre esse processo, commits e o futuro projeto da Vercel precisa ser implementada e autorizada separadamente. Nenhuma chave ou identidade de serviço é necessária para executar os testes deste repositório.
