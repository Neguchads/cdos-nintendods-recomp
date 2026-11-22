# RecompLauncher Integration — Castlevania: Dawn of Sorrow (ACVE)

Integração oficial com o ecossistema **RecompLauncher** (`format: 1`, schema v1).

## Como publicar e rodar pelo RecompLauncher (PT-BR)
1. Gere o pacote distribuível limpo (sem ROM proprietária):
   ```powershell
   python tools/package_recomplauncher.py
   ```
   O pacote final e o arquivo `.zip` ficam em `dist/castlevania-dos-recomp-win64/`, com verificação `SHA256SUMS.txt`.
2. No **RecompLauncher**, adicione a pasta do projeto (ou importe o `.zip`) contendo `recomplauncher.json`.
3. Quando solicitado pelo launcher, selecione a sua cópia original e legalmente dumpada de:
   - `Castlevania - Dawn of Sorrow (USA).nds` (64 MiB, `SHA-1: 47530ff87e608f88105a314fdf36dc385f8dec94`)
4. O pacote **nunca inclui nem redistribui ROMs proprietárias**. A tradução em Português (BR) é aplicada **apenas em memória** via patch delta binário [`mods/ptbr/dos-ptbr.dospatch`](../mods/ptbr/dos-ptbr.dospatch).
5. Por padrão, o jogo abre direto (`dos_skip_launcher=true`) e o menu gráfico **Dear ImGui** abre a qualquer momento com **`F1`** (`Esc` ou botão Guide no controle).

## Créditos da Tradução PT-BR
- Tradução Português (BR) v1.0 baseada em **romsportugues.com** (`Castlevania - Dawn of Sorrow (BR-USA) (DE) (T1.0)`), convertida em patch delta `DOSPATCH` sem alteração permanente da ROM USA original.

---

## Running with RecompLauncher (EN)
1. Stage a clean ROM-free release zip:
   ```powershell
   python tools/package_recomplauncher.py
   ```
2. Add the folder or release `.zip` (containing `recomplauncher.json`) to **RecompLauncher**.
3. Point RecompLauncher to your legally dumped USA `.nds` cartridge (`SHA-1: 47530ff87e608f88105a314fdf36dc385f8dec94`).
4. Both **UI Language** (`EN` / `PT-BR`) and **Game ROM Language** (`EN` / `PT-BR` in-memory delta patch) can be configured directly in RecompLauncher or toggled live inside the **`F1`** overlay menu.
