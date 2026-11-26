# Notas de Sessão (PR #35, Resposta aos Modders & Suporte Genérico a Mods Locais)

## Feito
- **PR #35 (`@Xarishark`) mergeado na `main` (`43d81e1`):** backup automático de `{data}/saves/definitive` e `{data}/saves/profiles`, `system` somente Windows e badge do RecompLauncher apontando direto para a página do jogo.
- **Issues `#43` (`@OerstedLAL`) e `#44` (`@Wet-Band-Aid`):** respostas respeitosas publicadas pedindo desculpas, esclarecendo que a intenção era suporte genérico a mods, confirmando a remoção de todos os mods de terceiros e perguntando canal de contato para futuras permissões formais.
- **Issue `#7` (Widescreen):** respondida e fechada (`completed`) referenciando a release `v1.2.0`.
- **Remoção completa de mods de terceiros & suporte genérico (`refactor/generic-mod-support`):**
  - Removidos do Git: `mods/ptbr/dos-ptbr.dospatch`, `mods/definitive/dos-definitive-{en,ptbr}.dospatch`, `mods/catalog.json`, `mods/reports/definitive-*.json`, `tools/fetch_community_mods.py` e todas as entradas de terceiros em `mods/registry.json`.
  - Adicionado importador offline genérico `tools/import_local_mod.py` (zero URLs/downloads).
  - `ndsrecomp/runner/src/dos_mod_registry.cpp` e `tools/mod_resolver.py` generalizados para descobrir automaticamente qualquer `*.dospatch` colocado pelo jogador em `{data}/mods/profiles/` com saves isolados; padrão alterado para `Original USA`.
  - `tools/package_recomplauncher.py` e `tools/rbs_artifact.py` endurecidos para rejeitar `.dospatch`/`.xdelta`/`.ips`/`.bps` em releases.
  - Verificado: `ctest` C++ `3/3` PASS (`0.55s`), `unittest` Python `55/55` PASS, `package_recomplauncher.py --validate-only` OK, `prepare_media_assets.py --check-only` OK, `patches/ndsrecomp-local.patch` (`1.55 MiB`, reverse-apply OK).

## Falta / Próximos passos
- Revisar diff, abrir PR, passar CI e mergear `refactor/generic-mod-support` na `main`; em seguida fechar `#43`, `#44` e `#19` com o commit exato de remoção.
- Decidir publicação de patch release `v1.2.1` clean-room (sem `.dospatch` de terceiros + `recomplauncher.json` do PR #35).
- Avaliar implementação da Issue `#39` (60Hz vertical sync sem crackle/pitch shift) e triagem das features de roadmap (`#30`, `#36`, `#37`, `#38`, `#40`).

## Decisões
- Nenhum mod ou tradução de terceiros será embutido, listado ou baixado automaticamente sem permissão explícita do autor; o projeto fornece exclusivamente suporte genérico local (`{data}/mods/profiles/*.dospatch` e `{data}/mods/music/`).
