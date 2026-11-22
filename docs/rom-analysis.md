# Análise da ROM — Castlevania: Dawn of Sorrow (USA, ACVE)

Mapeamento técnico extraído diretamente de `..\Roms\Castlevania - Dawn of Sorrow (USA).nds` usando `tools/prepare_rom.py` e `toolchains/dsd/dsd.exe` (`ds-decomp` v0.12.1).

## Identidade do Cartucho
- **Título no Header**: `CASTLEVANIA1`
- **Game Code**: `ACVE` (USA, Maker `A4`, Revision `0`)
- **Tamanho**: `67,108,864` bytes (`0x04000000`, 64 MiB)
- **SHA-1**: `47530ff87e608f88105a314fdf36dc385f8dec94`
- **SHA-256**: `3ddc8b0eac841b6005ff4c38a184b517fa8225ac905aad951b0572850358d8b0`
- **NitroSDK**: `0x02007532`
- **Save de Cartucho**: EEPROM 64 Kbit (`8192` bytes)

## Módulos Principais (ARM9 e ARM7)
- **ARM9 Principal** (descomprimido na ROM, `compressed_static_end = 0`):
  - ROM offset: `0x00004000`, RAM load: `0x02000000`, Entry PC: `0x02000800`, Tamanho: `0x000C6B98` (813,976 B)
  - Autoload `[0]` ITCM: `0x01FF8000` (`0x63C0` B, fonte `0x020C0740`) — 21 funções detectadas pelo `dsd`
  - Autoload `[1]` DTCM: `0x027C0000` (`0x80` B, fonte `0x020C6B00`)
  - Recompilação estática (`nds_recompile` com `reloc_scan`): **3.913 funções** (`3.905` ARM, `8` Thumb); `dsd` listou 2.421 funções e 6.319 símbolos totais em `analysis/dsd/project/arm9/symbols.txt`.
- **ARM7**:
  - ROM offset: `0x003B3E00`, RAM load: `0x02380000`, Entry PC: `0x02380000`, Tamanho: `0x00026654` (157,268 B)
  - `reloc_scan`: detectou cópias em `0x037F8000` (`0xF888` B, WRAM) e `0x027C0000` (`0x16C45` B)
  - Recompilação estática (`nds_recompile`): **1.268 funções** (`1.262` ARM, `6` Thumb).

## Overlays ARM9 (41 overlays, todos descomprimidos)
Total descoberto pelo `dsd` nos overlays: **3.317 funções**.

| Faixa de ID | Endereço RAM | Função no Jogo / `dsd` |
|---|---|---|
| `ov000` | `0x0219E3E0` (`0x92360` B) | Código constante núcleo 0 — **1.553 funções** (`dsd`) |
| `ov001` | `0x02230A00` (`0x69F20` B) | Código constante núcleo 1 — **1.156 funções** (`dsd`) |
| `ov002`..`ov005` | `0x0229A920`..`0x022D6E80` | Constantes de dados/tabelas — 0 funções (`dsd`) |
| `ov006`..`ov022` | `0x022DA4A0` (compartilhado) | Overlays de áreas do castelo (DSVEdit) — 0 funções (`dsd`), dados de sala/inimigos/tiles |
| `ov023`..`ov040` | `0x022FF9C0` (compartilhado) | Overlays dinâmicos (chefes / modos específicos) — **608 funções** no total (`dsd`) |

## Implicações para a Fase 2 (Promoção de Overlays)
- Na Fatia Vertical 1, `dos_arm9` e `dos_arm7` executam nativamente enquanto `ov000`, `ov001` e `ov023`..`ov040` caem no interpretador Tier-3 validado por bytes (`ndsrecomp`).
- Para a Fase 2, os candidatos prioritários para promoção estática (bancos validados por conteúdo) são **`ov000`** (1.553 funções) e **`ov001`** (1.156 funções), seguidos pelos overlays de chefes/modos `ov023`..`ov040`, usando os seeds já extraídos em `analysis/dsd/project/arm9/overlays/ov*/symbols.txt`.
- Os overlays `ov002`..`ov022` são puramente dados e não precisam de bancos recompilados.
