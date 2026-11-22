# Notas do Projeto — Castlevania: Dawn of Sorrow Recomp

## Metadados das ROMs verificados
- **ROM Base (USA):** `..\Roms\Castlevania - Dawn of Sorrow (USA).nds` — `67,108,864` bytes, SHA-1 `47530ff87e608f88105a314fdf36dc385f8dec94`, intacta.
- **ROM PT-BR de origem do patch:** `..\Roms\Castlevania - Dawn of Sorrow (BR-USA) (DE) (T1.0) (www.romsportugues.com).nds` — `67,108,864` bytes, SHA-1 `c9a1552bcdcd8fdf3c052d975e6838da7ead08d1`.
- **Diferenças estruturais medidas entre USA e PT-BR (`364.911` bytes no total):** `7 B` cabeçalho, `0 B` ARM7, `120 B` em ARM9 (`0x02008578..0x020c02f4`, hooks de acentuação), `3` overlays (`ov000`, `ov004`, `ov005`), e `88` arquivos NitroFS (fontes/textos).
- **Patch delta gerado:** `mods/ptbr/dos-ptbr.dospatch` (`469.280` bytes, `4.806` blocos) validado via SHA-1 + CRC32 sem modificar os arquivos `.nds` originais.

## Bug das 3 telas e reconstrução com Dear ImGui
- **Causa raiz anterior:** `present_screens` renderizava as 2 telas DS (`SideBySide` / `Stacked`) e depois desenhava `menu_texture` (`512x384` contendo cópia opaca de `raw_sources[hud_screen]`) por cima do centro do canvas, fazendo aparecer uma 3ª cópia da tela.
- **Solução aplicada:** `DosImGuiMenu` (Dear ImGui v1.92.9b) desenha diretamente sobre as 2 telas reais suspendendo temporariamente `SDL_SetRenderLogicalPresentation` para manter nitidez nativa (1080p+) e ignorando `menu_texture` / `g_runtime_menu_surface`.

## Verificações mais recentes (após última edição de código)
- `ctest`: **3/3 passaram** (`frontend_config_test`, `dos_enhancements_test`, `screen_layout_test`).
- `unittest`: **14/14 passaram** (`prepare_rom`, `promote_banks`, `ptbr_patch`, `recomplauncher`).
- `build.py smoke`: **PASS** (`724` vblanks, `report.json`).
- **DX12 GPU PT-BR (`420` frames limpo):** **`59,86 FPS`** (`emu=3,72 ms`, `pres=0,78 ms`, `rb=0,000 ms`, `underruns=0`).
- **Vulkan GPU SPIR-V PT-BR (`frame-240.png`):** ativo em hardware (`vulkan-gpu`, `SPIR-V Vulkan`), HUD completo sem cortes e imagem PT-BR validada visualmente.
- **Pacote RecompLauncher:** `dist/castlevania-dos-recomp-win64.zip` (`71.990.144` B) validado com `0` ROMs incluídas.
- **Publicação GitHub (`Neguchads/cdos-nintendods-recomp`):** `.gitignore`/`.gitattributes` endurecidos, `.github/dependabot.yml` (`github-actions` + `gradle`) e `.github/workflows/ci.yml` (`python-tests` Ubuntu/Windows + guarda clean-room + `shellcheck` + validação de patch/Android) configurados.
