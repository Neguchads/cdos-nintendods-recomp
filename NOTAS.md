# Notas de Sessão (Suíte Expandida de Gráficos & Display — ADR-016)

## Feito
- **Benchmark dos maiores recomps no GitHub por estrelas:** analisados `N64Recomp`, `Zelda64Recomp`, `UnleashedRecomp` e `zelda3` diretamente via `gh api` (`config_def.h`, `ui_config.cpp`, `config.h`).
- **Shader GPU expandido (`dos_postprocess.frag.hlsl` -> `DosShaderParams` 80 bytes, DXIL `ps_6_0` `16.496 B` + SPIR-V Vulkan 1.1 `33.420 B`):**
  - Novos controles ao vivo na GPU (custo zero nos padrões): **Gama** (`70..150%`), **Temperatura de Cor** (`-30..+30`), **Bloom Suave** (`0..50%`, bright-pass 8 taps), **Intensidade da Máscara** (`0..100%`) e **Curvatura CRT + bezel** (`0..30%`, `fwidth`-safe).
  - Validados ao vivo na RTX 3060 tanto em **Direct3D 12 (`dx12-gpu`)** quanto em **Vulkan (`vulkan-gpu`)** com 0 erros.
- **Display, Janela & Sincronização (`F1` EN + PT-BR + `recomplauncher.json`):**
  - **Seletor de Monitor SDL3** (`dos_display_index`, lista nome/resolução/Hz reais), **Escala da Janela** (`Auto`, `2x..6x` com clamp na área útil), **21:9 Ultrawide Cinema** (`ultrawide-21x9`), **Margem Segura / Overscan** (`0..10%`, mantendo toque exato), **Alinhamento do HUD Widescreen** (`Bordas 16:9` vs `Zona Segura 4:3`), **VSync 3 modos** (`Desligado`/`Ligado`/`Adaptativo` com fallback automático e retrocompatibilidade `0/1/false/true`), **Interpolação 120 Hz** ao vivo (`>= 100 Hz`), **3D MSAA** (`Off/2x/4x/8x`) persistente e **4 Perfis Visuais de 1 clique** (*HD Moderno Nítido*, *Pixel Purista*, *CRT Clássico*, *Portátil DS*).
- **Testes e Patch:** `ctest` `3/3` PASS (`dos_enhancements_test` + `frontend_config_test` + `screen_layout_test`), `unittest` `55/55` PASS, `package_recomplauncher.py --validate-only` OK, `prepare_media_assets.py --check-only` OK, `patches/ndsrecomp-local.patch` sincronizado (`1.422.202 B < 2 MiB`, `apply --check --reverse` OK) e `runtime/nds_runner.exe` atualizado.

## Falta / Próximos passos
- Decidir publicação de nova release (`v1.1.3` / `v1.2.0`) quando o usuário validar visualmente os novos presets e controles no `F1`.
- Corrigir movimento invertido no *Albus Mode* ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
- Zerar campanhas experimentais (*Eternity of Sorrow 1.2*, *Model ZX*, *Model Omega*) para promover a `verified`.

## Decisões
- **ADR-016:** Toda opção adicionada é 100% real em GPU/SDL3 (zero placebo), com `DosShaderParams` alinhado em 80 bytes (`5 × float4`), retrocompatibilidade total com arquivos `dos-settings.ini` antigos (`dos_vsync=0/1/false/true`) e derivadas `fwidth` fora de fluxo divergente em DX12 e Vulkan.
