# Custom Music (`mods/music/`)

Coloque qualquer arquivo **`.wav`**, **`.mp3`** ou **`.ogg`** (Vorbis) nesta pasta — **com qualquer nome!** — para substituir as músicas (BGMs) de *Castlevania: Dawn of Sorrow*, mantendo **100% dos efeitos sonoros (SFX) e vozes originais do DS**.

---

## 3 formas fáceis de configurar

### 1. Assistente gráfico com Windows Explorer (mais rápido)
Dê duplo clique em **`Configurar_Musica.bat`** dentro desta pasta (ou rode `python mods/music/configurar_musica.py`):
1. Abre a janela do Windows Explorer para escolher uma ou várias músicas (`.mp3`, `.wav`, `.ogg`) de qualquer pasta do PC.
2. Copia automaticamente para `mods/music/`.
3. Pergunta se você quer substituir **1 estágio específico (`#00..#29`)** ou ativar o **Modo Jukebox / Playlist Global** (muta todas as 30 BGMs do jogo e toca só as músicas selecionadas).
4. Salva tudo em `music.json`. Se o jogo já estiver aberto, aperte **F1 → Áudio → Reescanear Pasta `mods/music`**.

### 2. Direto dentro do jogo (`F1 → Áudio`)
1. Jogue seus arquivos `.mp3`, `.wav` ou `.ogg` nesta pasta (com qualquer nome).
2. Abra o menu **F1 → Áudio** e clique em **Reescanear Pasta `mods/music`**.
3. Escolha entre:
   - **Jukebox / Playlist Global**: marque **Modo Jukebox Global**, selecione 1 ou várias músicas na lista (com **Aleatório**, **Anterior** e **Próxima**) — muta todas as BGMs do DS e mantém SFX intacto.
   - **Substituir por Estágio**: escolha qualquer um dos 30 estágios (ou clique em **Sala Atual**), selecione o arquivo na lista e clique em **Aplicar neste Estágio**.

### 3. Automático por nome do arquivo ou `music.json` manual
Se preferir sem interface, basta começar o nome do arquivo pelo número da faixa (`00` a `29`):
- `07_file_select.mp3` → tela de **File Select** (`#07`)
- `11_pitch_black_intrusion.ogg` → primeira área **Lost Village** (`#11`)
- `02_boss1.wav` → **Boss 1 — Into the Dark Night** (`#02`)

Ou crie `music.json` manualmente nesta pasta:
```json
{
  "jukebox": {
    "enabled": false,
    "shuffle": false,
    "playlist": ["minha_musica_1.mp3", "minha_musica_2.ogg"]
  },
  "tracks": {
    "11": {
      "file": "minha_musica.ogg",
      "loop": true,
      "loop_start_ms": 4200,
      "loop_end_ms": 148000,
      "gain_db": -1.5
    }
  }
}
```

Para validar sua pasta no terminal:
```powershell
python tools\list_bgm_tracks.py --scan mods\music
```

## Catálogo das 30 faixas BGM (`00..29`)

| ID | Nome SDAT | Slug | Faixa |
|---|---|---|---|
| `00` | `SDL_BGM_ARR1_` | `vampire_killer_arr` | Vampire Killer (Arranged) |
| `01` | `SDL_BGM_ARR2_` | `bloody_tears_arr` | Bloody Tears (Arranged) |
| `02` | `SDL_BGM_BOSS1_` | `into_the_dark_night` | Into the Dark Night (Boss 1) |
| `03` | `SDL_BGM_BOSS2_` | `evil_invitation` | Evil Invitation (Boss 2) |
| `04` | `SDL_BGM_ENDING_` | `ending` | Ending Theme |
| `05` | `SDL_BGM_EV_BOSS_` | `event_boss` | Event Boss / Tension |
| `06` | `SDL_BGM_L2_BOSS_` | `final_boss_menace` | Final Boss (Menace) |
| `07` | `SDL_BGM_NAME_` | `file_select` | Name Entry / File Select |
| `08` | `SDS_BGM_OVER_` | `game_over` | Game Over |
| `09` | `SDL_BGM_PRE_` | `prelude` | Prelude / Prologue |
| `10` | `SDL_BGM_SHOP_` | `hammer_shop` | Hammer's Shop |
| `11` | `SDL_BGM_ST00_1_` | `pitch_black_intrusion` | Pitch Black Intrusion (Lost Village 1) |
| `12` | `SDL_BGM_ST00_2_` | `lost_village_2` | Lost Village (Interior) |
| `13` | `SDL_BGM_ST01_` | `draculas_tears` | Dracula's Tears (Wizardry Lab) |
| `14` | `SDL_BGM_ST02_` | `garden_of_madness` | Garden of Madness |
| `15` | `SDL_BGM_ST03_` | `dark_chapel` | Dark Chapel |
| `16` | `SDL_BGM_ST04_` | `demon_guest_house` | Demon Guest House |
| `17` | `SDL_BGM_ST05_` | `condemned_tower` | Condemned Tower |
| `18` | `SDL_BGM_ST06_` | `subterranean_hell` | Subterranean Hell |
| `19` | `SDL_BGM_ST07_` | `silenced_ruins` | Silenced Ruins |
| `20` | `SDL_BGM_ST08_` | `cursed_clock_tower` | Cursed Clock Tower |
| `21` | `SDL_BGM_ST09_` | `the_pinnacle` | The Pinnacle |
| `22` | `SDL_BGM_ST10_` | `mine_of_judgment` | Mine of Judgment |
| `23` | `SDL_BGM_ST11_` | `the_abyss` | The Abyss |
| `24` | `SDL_BGM_ST12_` | `abyss_depths` | Abyss Depths / Extra |
| `25` | `SDS_BGM_STAFF_` | `credits_staff` | Credits / Staff Roll |
| `26` | `SDL_BGM_TR_BOSS1_` | `boss_theme_3` | Scarlet Battle Soul (Boss 3) |
| `27` | `SDL_BGM_TR_BOSS2_` | `boss_theme_4` | Last Battle / Death & Julius |
| `28` | `SDL_BGM_WIND_` | `wind_ambience` | Wind Ambience |
| `29` | `SDL_BGM_YOKO_` | `yoko_shop` | Yoko's Soul Synthesis |
