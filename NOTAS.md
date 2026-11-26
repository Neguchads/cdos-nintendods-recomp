# Notas de Sessão (Escaladores 2D Modernos & Pipeline Multi-Passe HD-2D — ADR-018)

## Feito
- **Partes 1 + 2 entregues em pipeline multi-passe SDL3 GPU (`dos_gpu_shader.{h,cpp}`, `dos_postprocess.frag.hlsl`):**
  - **MMPX 2× (NVIDIA, 2021):** passe offscreen `2×` fiel a detalhes de 1 px (olhos, contornos, paleta intacta) seguido de `Pixellate` em sRGB linear (`0,6 ms` na GPU).
  - **OmniScale (SameBoy):** suavização perceptual de diagonais e cantos em 1 passe em sRGB linear (`0,6 ms` na GPU).
  - **ScaleFX-Hybrid 3×:** reconstrução vetorial de silhuetas `3×` + reverse-AA sutil no interior, seguido de `Pixel-AA` em sRGB linear (`0,8 ms` na GPU).
  - **Anti-Dither Seletivo (GDAPT, `dos_anti_dither`):** pré-passe opcional em sRGB linear que suaviza padrões xadrez/listras de 1 px sem borrar contornos nem texto.
  - **Bloom HD-2D Dual Kawase (5 passes reais):** pirâmide `1/2 -> 1/4 -> 1/8 -> 1/4 -> 1/2` + composição aditiva (`pass_mode = 9`, `SDL_BLENDMODE_ADD`) alinhada à curvatura CRT, bezel e vinheta (`0,8 ms` total).
  - **Menu `F1 -> Gráficos HD` & `recomplauncher.json`:** 8 filtros curados (`Pixellate` continua padrão), toggle `Anti-Dither Seletivo`, e 2 novos Perfis Visuais de 1 clique (**Remaster HD-2D (Bloom)** e **Vetor HD (ScaleFX)**).
- **Compactação do Ubershader & Patch:** headers DXIL (`56.272 B`) e SPIR-V `-Os` (`91.884 B`) gravados em `uint32_t` little-endian, mantendo `patches/ndsrecomp-local.patch` em **`1.620.341 B` (`1,55 MiB < 2,00 MiB`)** com `git apply --check --reverse` limpo.
- **Verificação:** `ctest` `3/3` PASS (0 warnings), 5 testes ao vivo na RTX 3060 PASS em `dx12-gpu` e `vulkan-gpu` (incluindo todos os 9 passes simultâneos), inspeção visual real de capturas DX12 (`hd2d_title.png`, `scalefx_title.png`, `mmpx_title.png`), `unittest` `55/55` PASS, `package_recomplauncher.py --validate-only` OK, `prepare_media_assets.py --check-only` OK, e `runtime/nds_runner.exe` atualizado.

## Falta / Próximos passos
- Validar visualmente no jogo os perfis **Remaster HD-2D** e **Vetor HD (ScaleFX)** e decidir empacotamento/publicação da release **`v1.2.0`** no GitHub.
- Opcional futuro: carregador de pacotes de texturas HD por hash na `GPU3D` (estilo *Ship of Harkinian* / *Mesen HD*) e correção do *Albus Mode* (Issue #19).

## Decisões
- **ADR-018:** Ubershader único compacto (`num_samplers = 1`, `DosShaderParams` mantido em 80 bytes reaproveitando `_pad[3]`) + pool de 20 `SDL_GPURenderState*` (zero colisão de uniform buffers entre passes) + `grid_div` mantendo Scanlines/CRT/LCD travados nas 192 linhas do DS mesmo após `MMPX 2×` / `ScaleFX 3×`.
