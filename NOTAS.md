# Notas de Sessão (Widescreen 2D Nativo Sem Cortes & Upscalers Curados — ADR-017)

## Feito
- **Widescreen 2D Nativo `342×192` perfeito (sem faixas pretas nem emendas):**
  - Diagnóstico ao vivo em RAM/VRAM na Ponte (`0x022DD9F8`) e Praça (`0x022DFCF8`) da Lost Village revelou dois cortes distintos: (1) fundo paralaxe `k=2` (`1×2`, `flags=0x01A0`) é `BG2` 2D em hardware cujo screenblock 1 (`x=256..511`) ficava zerado -> adicionado wrap módulo 256 em `gpu2d.{h,cpp}` ativado por `title_patches.cpp`; (2) quad 3D atmosférico sem textura `sub=1` (`x=0..271, y=0..192, alpha=10`) era rasterizado via `native_3d_raster.cpp` -> adicionada expansão limpa para `RenderWidth` (`342`) em `native_3d_raster.cpp` (e fallback `GPU3D.cpp`) alocando vértices próprios sem alterar vértices compartilhados.
  - Validado visualmente em `v4_plaza_fixed.png` e `v4_bridge_fixed.png`: `delta(271-270) = (0, 0, 0)`, céu/lua/castelo/névoa contínuos de `x = 0` até `x = 341`.
- **Upscalers Pixel-Art Curados em Luz Linear & Menu `F1` Enxuto:**
  - `dos_postprocess.frag.hlsl` recompilado para DXIL `ps_6_0` (`20.812 B`) e Vulkan 1.1 SPIR-V (`38.200 B`): novos **`Pixellate`** (área analítica exata 1.0 px em sRGB linear IEC 61966-2-1, **novo padrão**), **`Pixel-AA`** (smoothstep cúbico 1.5 px) e **`Bandlimited Pixel`** aprimorado (integral de cosseno TheMaister em sRGB linear); `Sharpen` corrigido para centros `±1` texel (padrão `Off`); `Scanlines`/`CRT`/`LCD` em ondas cosseno analíticas sem moiré atenuadas por `fwidth` pré-clamp.
  - Dropdown curado para os 5 filtros sem artefatos (`Pixellate`, `Pixel-AA`, `Bandlimited Pixel`, `Nearest`, `Bilinear`) em `dos_imgui_menu.cpp`, `game.toml` e `recomplauncher.json`, mantendo retrocompatibilidade de INI (`xbr2x`/`scale2x`/`sharp-bilinear`), seção *Calibração Avançada* recolhível, curvatura CRT condicional e PiP preservando filtros nítidos.
- **Verificação:** `ctest` `3/3` PASS (`dos_enhancements_test` + `frontend_config_test` + `screen_layout_test`), RTX 3060 ao vivo PASS em `dx12-gpu` (`DXIL ps_6_0`) e `vulkan-gpu` (`SPIR-V Vulkan`), `unittest` `55/55` PASS, `package_recomplauncher.py --validate-only` OK, `prepare_media_assets.py --check-only` OK, `patches/ndsrecomp-local.patch` sincronizado (`1.496.741 B < 2 MiB`, `apply --check --reverse` OK) e `runtime/nds_runner.exe` atualizado.

## Falta / Próximos passos
- Se o jogador já tinha `dos_hd_filter=xbr2x` salvo no `dos-settings.ini` local, escolher **Pixellate** (ou clicar **HD Moderno Nítido**) em `F1 -> Gráficos HD`.
- Decidir publicação de nova release (`v1.2.0`) após validação visual do usuário.
- Corrigir movimento invertido no *Albus Mode* ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).

## Decisões
- **ADR-017:** Priorizar qualidade visual real em vez de quantidade de filtros: `Pixellate` em sRGB linear como padrão universal, remoção de `xBR 2x`/`Scale2x` do dropdown principal (mantendo leitura legada de INI) e correção na raiz tanto do wrap 2D `BG2` quanto da expansão de quads atmosféricos no pipeline `native_3d_raster.cpp`.
