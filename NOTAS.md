# Notas de Sessão (Suporte Nativo `.xdelta`/`.ips` & VSync 60Hz Sem Mudar Tom)

## Feito
- **Suporte nativo `.xdelta` / `.vcdiff` e `.ips` direto no `nds_runner.exe` (`dos_rom_patch.cpp`, `dos_mod_registry.cpp`, `tools/mod_resolver.py`):**
  - Decodificadores C++ puros RFC 3284 VCDIFF (COPY/ADD/RUN + Adler32, com fallback automático para `xdelta3.exe` via `CreateProcessW` quando usa compressor secundário DJW/LZMA) e IPS (Hunk + RLE + truncation), além de diagnóstico claro para XDELTA1 legado (`%XDZ00x%`).
  - Auto-descoberta em `{data}/mods/profiles/` para `.dospatch`, `.xdelta`, `.vcdiff`, `.xdelta3` e `.ips` com saves/savestates isolados e proteção de IDs reservados.
- **Issue `#39` — Modo VSync Exato `60.0 Hz` (`sync60`):**
  - Novo `DosVsyncMode::Sync60Hz` em `dos_enhancements.{h,cpp}`, `dos_i18n.{h,cpp}`, `dos_imgui_menu.cpp`, `frontend.cpp` e `recomplauncher.json`.
  - `DosPitchPreservingAudioSync` (WSOLA overlap-add de janela Hann 128 frames): elimina o micro-stutter do clock DS `59.8261 Hz` em LCD 60 Hz com zero crackle e 0.00% alteração de pitch (validado em teste de 600 frames a 440 Hz).

## Falta / Próximos passos
- Abrir PR, passar revisão + CI e mergear `feat/xdelta-ips-and-60hz-vsync`, respondendo/fechando `#39` e respondendo `#30` com instruções de uso do `.xdelta` local.
- Atacar próximas fatias das issues abertas: `#37` (Cheat Manager), `#38` (Advanced Custom Music Manager), `#36` (Texture Dumping/HD Packs) e análise/resposta técnica de `#40` (Multi-idioma EUR), além da patch release clean-room `v1.2.1`.

## Decisões
- WSOLA de janela Hann (128 samples, busca de fase correlacionada em `[96..256]`) escolhido em vez de `SDL_SetAudioStreamFrequencyRatio` para cumprir literalmente o requisito de **0.00% alteração de tom** na Issue `#39`.
