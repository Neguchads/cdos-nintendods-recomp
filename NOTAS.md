# Notas de Sessão (Slots Pré-Configurados PT-BR v1.1 & Mods + Botões Rápidos no Menu F1)

## Feito
- **Botões rápidos por mod no `F1 -> Mods & Campanhas` (`dos_imgui_menu.{h,cpp}`, `dos_i18n.{h,cpp}`, `dos_mod_registry.{h,cpp}`, `frontend.cpp`):**
  - Cada slot `manual_import` agora exibe inline **`Aplicar Patch...`** (abre o seletor SDL3 já direcionado ao ID do slot, aceitando qualquer nome de arquivo `.xdelta`/`.ips`/`.dospatch`, instalando como `<slot_id><ext>`, limpando extensões antigas, selecionando a campanha e exibindo toast) e **`Site Oficial`** (abre somente URLs `https://` no navegador do sistema).
  - Mantido o botão genérico **`Importar Patch (.xdelta / .ips / .dospatch)...`** + **`Abrir Pasta de Mods`** para qualquer outro mod comunitário.
- **Slots clean-room `manual_import: true` em `mods/registry.json` (zero arquivos embutidos):**
  - **Tradução PT-BR v1.1 (Vanilla)** (`cdos-ptbr-v1-1`, casa `cdos_1.1.xdelta`) e **Tradução PT-BR v1.1 (Definitive Edition)** (`cdos-ptbr-de-v1-1`, casa `cdos_de_1.1.xdelta`) — equipe completa (**Hyllian, Solid One/`@leomontenegro6`, Neko Belmont, Mysterioso, denim, djmatheusito, victoriemini** + repo oficial `leomontenegro6/cdos-traducao-ptbr` + **João13 Traduções**).
  - **Definitive Edition+**, **Eternity of Sorrow** (`@Wet-Band-Aid`, autorizado #44), **Alucard's Requiem (SOTN & CV3)** e **Dracula's Curse (Trevor Mode)**.
  - Mods de `@OerstedLAL` permanecem 100% excluídos (conforme pedido na Issue #43).
- **Créditos & Pedidos de Permissão:** `docs/CREDITS.md` completo e `docs/CREATOR_OUTREACH.md` com mensagens prontas para enviar a cada criador após aprovação.

## Falta / Próximos passos
- Compilar, rodar `ctest` + `unittest`, sincronizar `patches/ndsrecomp-local.patch`, abrir PR, revisar diff com subagente + CI e mergear na `main`.
- Gerar e publicar a release clean-room `v1.2.1` após limpeza da pasta temporária em `dist/` e confirmação do usuário.

## Decisões
- `SDL_OpenURL` no botão **`Site Oficial`** valida estritamente o prefixo `https://` para impedir execução de esquemas locais/arbitrários vindos de JSON editado.
- Preferir match por slug de ID (`<id>.*`) antes de `profile_file` no rescan C++/Python para que um patch importado pelo botão rápido sempre sobreponha um arquivo antigo solto na pasta.
