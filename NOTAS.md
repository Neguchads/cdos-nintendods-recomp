# Notas de Sessão (Importador In-Game de Patches & Minimap HUD Samus Returns 16:9)

## Feito
- **Importador nativo de mods dentro do `F1 -> Mods & Campanhas` (`frontend.cpp`, `dos_imgui_menu.{h,cpp}`, `dos_mod_registry.{h,cpp}`, `dos_i18n.{h,cpp}`):**
  - Botão **`Importar Patch (.xdelta / .ips / .dospatch)...`** abre o seletor nativo SDL3 (`SDL_ShowOpenFileDialog`), valida assinatura binária (`VCDIFF`, `IPS`, `DOSPATCH`; rejeita `XDELTA1` legado e IDs reservados), copia atomicamente para `{data}/mods/profiles/<slug><ext>`, dispara rescan imediato e exibe toast.
  - Botão **`Abrir Pasta de Mods`** garante a criação de `{data}/mods/profiles/` e abre no Explorer via `SDL_OpenURL` (URI `file:///` com percent-encoding UTF-8).
  - Slot de compatibilidade `manual_import: true` para **Eternity of Sorrow** (`@Wet-Band-Aid`, autorização explícita na Issue `#44`, zero arquivos embutidos ou baixados) + créditos em `docs/CREDITS.md` + casamento automático por slug em C++ (`dos_mod_registry.cpp`) e Python (`tools/mod_resolver.py`).
- **Layout `Minimap HUD (Samus Returns 16:9)` & Preset 1-Clique (`screen_layout.h`, `dos_enhancements.cpp`, `frontend_config.cpp`, `frontend.cpp`, `dos_imgui_menu.cpp`, `recomplauncher.json`):**
  - Novo `NdsScreenLayout::MinimapHud` (`minimap-hud`, aliases `minimap`/`samus`/`metroidvania`): tela principal `342×192` + minimapa compacto de `24%` no canto (margem `4 px`, escala configurável `16..50%`), incluído no ciclo `F2` e no manifesto do RecompLauncher.
  - Botão **1 Clique: HUD Metroidvania 16:9** ativa `True 2D Widescreen` + `Minimap HUD` + `Top-Right` + `80%` opacidade + `Edge-Anchored` HUD.

## Falta / Próximos passos
- Compilar `dos_enhancements_test` + `nds_runner`, rodar `ctest` + `unittest` + validadores de manifesto/mídia, sincronizar `patches/ndsrecomp-local.patch`, abrir PR, rodar revisão de diff por subagente + CI e fazer squash-merge na `main`.
- Gerar e publicar a release patch clean-room `v1.2.1` substituindo o ZIP antigo da `v1.2.0` (que ainda continha `.dospatch` de terceiros).

## Decisões
- Fila estática protegida por `std::mutex` + `std::atomic<bool>` para o callback assíncrono do `SDL_ShowOpenFileDialog`, evitando ponteiro pendente caso a janela feche antes do diálogo nativo do Windows.
- `SDL_OpenURL` com URI `file:///` percent-encoded em vez de incluir `<windows.h>` no `frontend.cpp` (evita conflitos de macros Win32 e mantém portabilidade Linux/Windows).
