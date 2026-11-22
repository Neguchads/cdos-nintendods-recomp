# ROM Analysis / Análise da ROM: Castlevania: Dawn of Sorrow (USA, ACVE)

**[English](#english) | [Português (BR)](#português-br)**

---

## English

Technical map extracted directly from `..\Roms\Castlevania - Dawn of Sorrow (USA).nds` with `tools/prepare_rom.py` and `toolchains/dsd/dsd.exe` (`ds-decomp` v0.12.1).

### Cartridge identity

- **Header title:** `CASTLEVANIA1`
- **Game code:** `ACVE` (USA, maker `A4`, revision `0`)
- **Size:** `67,108,864` bytes (`0x04000000`, 64 MiB)
- **CRC32:** `135737f6` (used by RecompLauncher for the verified badge)
- **SHA-1:** `47530ff87e608f88105a314fdf36dc385f8dec94`
- **SHA-256:** `3ddc8b0eac841b6005ff4c38a184b517fa8225ac905aad951b0572850358d8b0`
- **NitroSDK:** `0x02007532`
- **Cartridge save:** 64 Kbit EEPROM (`8192` bytes)

### Main modules (ARM9 and ARM7)

- **Main ARM9** (uncompressed in the ROM, `compressed_static_end = 0`):
  - ROM offset `0x00004000`, RAM load `0x02000000`, entry PC `0x02000800`, size `0x000C6B98` (813,976 B)
  - Autoload `[0]` ITCM: `0x01FF8000` (`0x63C0` B, source `0x020C0740`), 21 functions found by `dsd`
  - Autoload `[1]` DTCM: `0x027C0000` (`0x80` B, source `0x020C6B00`)
  - Static recompilation (`nds_recompile` with `reloc_scan`): **3,913 functions** (`3,905` ARM, `8` Thumb); `dsd` listed 2,421 functions and 6,319 symbols in `analysis/dsd/project/arm9/symbols.txt`
- **ARM7**:
  - ROM offset `0x003B3E00`, RAM load `0x02380000`, entry PC `0x02380000`, size `0x00026654` (157,268 B)
  - `reloc_scan` found copies to `0x037F8000` (`0xF888` B, WRAM) and `0x027C0000` (`0x16C45` B)
  - Static recompilation (`nds_recompile`): **1,268 functions** (`1,262` ARM, `6` Thumb)

### ARM9 overlays (41 overlays, all uncompressed)

`dsd` found **3,317 functions** in the overlays.

| ID range | RAM address | Role in the game / `dsd` |
|---|---|---|
| `ov000` | `0x0219E3E0` (`0x92360` B) | Core code 0: **1,553 functions** |
| `ov001` | `0x02230A00` (`0x69F20` B) | Core code 1: **1,156 functions** |
| `ov002`..`ov005` | `0x0229A920`..`0x022D6E80` | Data / tables: 0 functions |
| `ov006`..`ov022` | `0x022DA4A0` (shared) | Castle area overlays (DSVEdit): 0 functions; room / enemy / tile data |
| `ov023`..`ov040` | `0x022FF9C0` (shared) | Dynamic overlays (bosses / special modes): **608 functions** in total |

### Static bank promotion

- In vertical slice 1, `dos_arm9` and `dos_arm7` ran natively while `ov000`, `ov001` and `ov023`..`ov040` fell to the content-validated Tier-3 interpreter (`ndsrecomp`).
- In phase 2, `ov000` (1,553 functions) and `ov001` (1,156 functions) were promoted first, then the boss / mode overlays `ov023`..`ov040`, using the `dsd` seeds in `analysis/dsd/project/arm9/overlays/ov*/symbols.txt`. Total: `34` banks, `49,059` functions.
- `ov002`..`ov022` are pure data and need no recompiled banks.
- The PT-BR translation changes `ov000`, `ov004` and `ov005`; `dos_arm9` / `dos_arm7` are built with `--validate-live-bytes` so changed functions fall back to the interpreter.

[Voltar ao topo / Back to top](#rom-analysis--análise-da-rom-castlevania-dawn-of-sorrow-usa-acve)

---

## Português (BR)

Mapeamento técnico extraído diretamente de `..\Roms\Castlevania - Dawn of Sorrow (USA).nds` com `tools/prepare_rom.py` e `toolchains/dsd/dsd.exe` (`ds-decomp` v0.12.1).

### Identidade do cartucho

- **Título no header:** `CASTLEVANIA1`
- **Game code:** `ACVE` (USA, maker `A4`, revisão `0`)
- **Tamanho:** `67.108.864` bytes (`0x04000000`, 64 MiB)
- **CRC32:** `135737f6` (usado pelo RecompLauncher para o selo de verificado)
- **SHA-1:** `47530ff87e608f88105a314fdf36dc385f8dec94`
- **SHA-256:** `3ddc8b0eac841b6005ff4c38a184b517fa8225ac905aad951b0572850358d8b0`
- **NitroSDK:** `0x02007532`
- **Save do cartucho:** EEPROM 64 Kbit (`8192` bytes)

### Módulos principais (ARM9 e ARM7)

- **ARM9 principal** (descomprimido na ROM, `compressed_static_end = 0`):
  - Offset na ROM `0x00004000`, carga na RAM `0x02000000`, PC de entrada `0x02000800`, tamanho `0x000C6B98` (813.976 B)
  - Autoload `[0]` ITCM: `0x01FF8000` (`0x63C0` B, fonte `0x020C0740`), 21 funções detectadas pelo `dsd`
  - Autoload `[1]` DTCM: `0x027C0000` (`0x80` B, fonte `0x020C6B00`)
  - Recompilação estática (`nds_recompile` com `reloc_scan`): **3.913 funções** (`3.905` ARM, `8` Thumb); o `dsd` listou 2.421 funções e 6.319 símbolos em `analysis/dsd/project/arm9/symbols.txt`
- **ARM7**:
  - Offset na ROM `0x003B3E00`, carga na RAM `0x02380000`, PC de entrada `0x02380000`, tamanho `0x00026654` (157.268 B)
  - O `reloc_scan` detectou cópias para `0x037F8000` (`0xF888` B, WRAM) e `0x027C0000` (`0x16C45` B)
  - Recompilação estática (`nds_recompile`): **1.268 funções** (`1.262` ARM, `6` Thumb)

### Overlays ARM9 (41 overlays, todos descomprimidos)

O `dsd` encontrou **3.317 funções** nos overlays.

| Faixa de ID | Endereço RAM | Função no jogo / `dsd` |
|---|---|---|
| `ov000` | `0x0219E3E0` (`0x92360` B) | Código núcleo 0: **1.553 funções** |
| `ov001` | `0x02230A00` (`0x69F20` B) | Código núcleo 1: **1.156 funções** |
| `ov002`..`ov005` | `0x0229A920`..`0x022D6E80` | Dados / tabelas: 0 funções |
| `ov006`..`ov022` | `0x022DA4A0` (compartilhado) | Overlays de áreas do castelo (DSVEdit): 0 funções; dados de sala / inimigos / tiles |
| `ov023`..`ov040` | `0x022FF9C0` (compartilhado) | Overlays dinâmicos (chefes / modos específicos): **608 funções** no total |

### Promoção estática de bancos

- Na fatia vertical 1, `dos_arm9` e `dos_arm7` rodavam nativamente enquanto `ov000`, `ov001` e `ov023`..`ov040` caíam no interpretador Tier-3 validado por conteúdo (`ndsrecomp`).
- Na fase 2, `ov000` (1.553 funções) e `ov001` (1.156 funções) foram promovidos primeiro, depois os overlays de chefes / modos `ov023`..`ov040`, usando os seeds do `dsd` em `analysis/dsd/project/arm9/overlays/ov*/symbols.txt`. Total: `34` bancos, `49.059` funções.
- Os overlays `ov002`..`ov022` são só dados e não precisam de bancos recompilados.
- A tradução PT-BR altera `ov000`, `ov004` e `ov005`; `dos_arm9` / `dos_arm7` são gerados com `--validate-live-bytes` para que funções alteradas caiam no interpretador.

[Voltar ao topo / Back to top](#rom-analysis--análise-da-rom-castlevania-dawn-of-sorrow-usa-acve)
