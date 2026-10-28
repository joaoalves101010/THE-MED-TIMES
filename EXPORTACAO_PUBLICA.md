# Escopo da exportação pública

Snapshot da edição **006**, de **2026-10-28**, com código-fonte portátil e saída estática. Páginas e recursos de leitura são copiados sem alteração dos fatos, datas, créditos ou conteúdo. A reconstrução limpa deve produzir exatamente os mesmos arquivos públicos.

## Exceções intencionais

Não exportar metadados de ambiente/plataforma, histórico Git privado, credenciais, caches, provas descartadas, registros brutos de revisão, manifestações de release internas, evidências privadas ou diretórios de proveniência — inclusive em snapshots de edições antigas. Esses registros não fazem parte da navegação pública.

Remover campos de caminho local de metadados fotográficos, preservando direitos, créditos e origem. Miniaturas antigas não referenciadas podem ser omitidas; todas as imagens usadas pelo arquivo e os registros necessários para reconstrução permanecem intactos.

A configuração usa a identidade portátil `the-med-times`. Recursos-fonte ficam em `src/assets/`; miniaturas são identificadas pelo conteúdo e conferidas por hashes. A validação na hospedagem é Node sem dependências; renderizar uma miniatura nova localmente requer bibliotecas gráficas opcionais.

Manter licenças e textos editoriais. Uma ocorrência inesperada de dado privado deve interromper a exportação, nunca ser ocultada por alteração silenciosa de uma matéria.
