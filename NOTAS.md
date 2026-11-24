# Notas de Sessão (Sharp Scaling & True 2D Widescreen `342×192`)

## Feito
- **Shaders anti-cintilação para esticar sem perder qualidade (`dos_postprocess.frag.hlsl` -> DXIL `ps_6_0` + SPIR-V Vulkan 1.1):**
  - `Sharp Bilinear` (`filter_mode = 2u`) evoluído para prescale inteiro automático independente por eixo + transição subpixel via `fwidth`.
  - Novo `Bandlimited Pixel` (`filter_mode = 5u`, `bandlimited-pixel`) com degrau quíntico C2 + mistura linear gama 2.0 para eliminar cintilação no scroll em qualquer proporção (`16:9`, `16:10`, `21:9`, janela livre).
  - Validados ao vivo na RTX 3060 em `dx12-gpu` (DXIL `ps_6_0`) e `vulkan-gpu` (SPIR-V Vulkan).
- **Widescreen 2D Nativo Real `16:9` (`342×192`, opt-in Experimental):**
  - Alternável ao vivo em `F1 -> Tela & Layout` (`dos_true_widescreen`, padrão `false`) e em `recomplauncher.json`.
  - 14 ganchos ARM9 verificados com preflight em `title_patches.cpp` (projeção 3D ortográfica `-171..+171`, aspecto `342/192`, colunas BG `17 -> 23`, clear BG2 `0x600 -> 0x1000`, centro de câmera `171`, clamp `cam_max_x`, OAM cull `344`) + amostragem direta `0..341` de BG2 `64×32` (`512px`) em `gpu2d.cpp`.
  - Detecção automática de gameplay (`g_state[0x08] == 0x02` && `width_screens >= 2`): prólogo (`0x01`), menu de pausa/equip (`0x0A`), tela título e Save Rooms (`width_screens == 1`) ficam em `256×192` centralizado limpo, e o HUD HP/MP fica 100% íntegro no canto superior esquerdo (`center_width = 8`).
- **`v1.1.2` publicada (anterior nesta sessão):** launcher MSVC 2022 (`443 KB`, 5 DLLs do Windows), allowlist explícita de `runtime/`, SHA-256 obrigatório em `dsd.exe`, preset portável `-march=x86-64 -mtune=generic`.
- `patches/ndsrecomp-local.patch` sincronizado (`1,343,511 B < 2 MiB`, `apply --check --reverse` OK) e `runtime/nds_runner.exe` atualizado localmente.

## Falta / Próximos passos
- Testar `True 2D Widescreen 342×192` em mais salas/chefes do castelo (e decidir quando promover a próxima tag `v1.1.3` / `v1.2.0`).
- Corrigir movimento invertido no *Albus Mode* ([Issue #19](https://github.com/Neguchads/cdos-nintendods-recomp/issues/19)).
- Zerar campanhas experimentais (*Eternity of Sorrow 1.2*, *Model ZX*, *Model Omega*) para promover de `unverified` para `verified`.

## Decisões
- **ADR-015:** `Sharp Bilinear` (auto-integer) + `Bandlimited Pixel` (C2 quintic) resolvem esticamento nítido sem distorção em qualquer formato mantendo `DosShaderParams` em 48 bytes; `True 2D Widescreen 342×192` aproveita o pipeline híbrido nativo de *Dawn of Sorrow* (GPU3D ortográfica + BG2 `64×32` + OAM HUD) com preflight estrito e fallback automático para `256×192` fora de gameplay multi-tela.
