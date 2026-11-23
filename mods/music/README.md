# Custom Music Guide / Guia de Música Customizada (`mods/music/`)

**[English](#english) | [Português (BR)](#português-br)**

---

<a id="english"></a>

## English

Drop your own **`.wav`**, **`.mp3`**, or **`.ogg`** (Vorbis) remixes/covers into `{data}/mods/music/` (in standalone builds, this folder right here: `mods/music/`). The runner automatically detects the active BGM via the DS Nitro SDK sound driver, silences **only** the DS music channel (`player 0`), and mixes your custom track in real time while keeping **100% of original DS sound effects and voices**.

### File Naming (Zero Config Needed)
Name any file using **any** of these formats:
- **Track ID:** `11.mp3`, `11.ogg`, `11_my_remix.wav`
- **SDAT name:** `SDL_BGM_ST00_1_.mp3` or `SDL_BGM_ST00_1.ogg`
- **Friendly slug:** `pitch_black_intrusion.mp3`, `draculas_tears.ogg`, `into_the_dark_night.wav`

After adding files, press **`F1` → Audio → Rescan `mods/music` Folder** (no restart needed).

### Optional `music.json` (Custom Loop Points & Volume)
Create `mods/music/music.json` if you want exact millisecond loop points or per-track gain:

```json
{
  "tracks": {
    "11": {
      "file": "pitch_black_metal_cover.ogg",
      "loop": true,
      "loop_start_ms": 4200,
      "loop_end_ms": 112500,
      "gain_db": -1.5
    },
    "SDL_BGM_BOSS1_": {
      "file": "boss1_orchestral.mp3",
      "loop": true,
      "gain_db": 0.0
    }
  }
}
```

### All 30 Dawn of Sorrow BGM Tracks

| ID | SDAT Name | Friendly Slug | Area / Theme | Default Loop |
|---:|---|---|---|:---:|
| `00` | `SDL_BGM_ARR1_` | `vampire_killer_arr` | Vampire Killer (Arranged) | Yes |
| `01` | `SDL_BGM_ARR2_` | `bloody_tears_arr` | Bloody Tears (Arranged) | Yes |
| `02` | `SDL_BGM_BOSS1_` | `into_the_dark_night` | Into the Dark Night (Boss 1) | Yes |
| `03` | `SDL_BGM_BOSS2_` | `evil_invitation` | Evil Invitation (Boss 2) | Yes |
| `04` | `SDL_BGM_ENDING_` | `ending` | Ending Theme | No |
| `05` | `SDL_BGM_EV_BOSS_` | `event_boss` | Event Boss / Tension | Yes |
| `06` | `SDL_BGM_L2_BOSS_` | `final_boss_menace` | Final Boss (Menace) | Yes |
| `07` | `SDL_BGM_NAME_` | `file_select` | Name Entry / File Select | Yes |
| `08` | `SDS_BGM_OVER_` | `game_over` | Game Over | No |
| `09` | `SDL_BGM_PRE_` | `prelude` | Prelude / Prologue | Yes |
| `10` | `SDL_BGM_SHOP_` | `hammer_shop` | Hammer's Shop | Yes |
| `11` | `SDL_BGM_ST00_1_` | `pitch_black_intrusion` | Pitch Black Intrusion (Lost Village 1) | Yes |
| `12` | `SDL_BGM_ST00_2_` | `lost_village_2` | Lost Village (Interior) | Yes |
| `13` | `SDL_BGM_ST01_` | `draculas_tears` | Dracula's Tears (Wizardry Lab) | Yes |
| `14` | `SDL_BGM_ST02_` | `garden_of_madness` | Garden of Madness | Yes |
| `15` | `SDL_BGM_ST03_` | `dark_chapel` | Dark Chapel (Chapel) | Yes |
| `16` | `SDL_BGM_ST04_` | `demon_guest_house` | Demon Guest House | Yes |
| `17` | `SDL_BGM_ST05_` | `condemned_tower` | Condemned Tower | Yes |
| `18` | `SDL_BGM_ST06_` | `subterranean_hell` | Subterranean Hell | Yes |
| `19` | `SDL_BGM_ST07_` | `silenced_ruins` | Silenced Ruins | Yes |
| `20` | `SDL_BGM_ST08_` | `cursed_clock_tower` | Cursed Clock Tower | Yes |
| `21` | `SDL_BGM_ST09_` | `the_pinnacle` | The Pinnacle | Yes |
| `22` | `SDL_BGM_ST10_` | `mine_of_judgment` | Mine of Judgment | Yes |
| `23` | `SDL_BGM_ST11_` | `the_abyss` | The Abyss | Yes |
| `24` | `SDL_BGM_ST12_` | `abyss_depths` | Abyss Depths / Extra | Yes |
| `25` | `SDS_BGM_STAFF_` | `credits_staff` | Credits / Staff Roll | No |
| `26` | `SDL_BGM_TR_BOSS1_` | `boss_theme_3` | Scarlet Battle Soul (Boss 3) | Yes |
| `27` | `SDL_BGM_TR_BOSS2_` | `boss_theme_4` | Last Battle / Death & Julius | Yes |
| `28` | `SDL_BGM_WIND_` | `wind_ambience` | Wind Ambience | Yes |
| `29` | `SDL_BGM_YOKO_` | `yoko_shop` | Yoko's Soul Synthesis | Yes |

> Tip: Check your folder with `python tools/list_bgm_tracks.py --scan mods/music`.

---

<a id="português-br"></a>

## Português (BR)

Coloque seus próprios arquivos **`.wav`**, **`.mp3`** ou **`.ogg`** (Vorbis) em `{data}/mods/music/` (no executável standalone, esta pasta `mods/music/`). O runtime identifica automaticamente a música ativa no driver de som do DS, silencia **somente** o canal de música (`player 0`) e mixa sua faixa ao vivo mantendo **100% dos efeitos sonoros (SFX) e vozes originais**.

- **Nomeação automática:** use o ID (`11.mp3`, `11_meu_remix.ogg`), o nome SDAT (`SDL_BGM_ST00_1_.wav`) ou o slug (`pitch_black_intrusion.mp3`).
- **Recarga ao vivo:** no jogo, abra **`F1` → Áudio → Reescanear Pasta `mods/music`** (não precisa reiniciar). O menu também mostra ao vivo qual faixa está tocando na sala atual.
- **Loop exato opcional:** crie `mods/music/music.json` usando o formato acima (`loop_start_ms`, `loop_end_ms`, `gain_db`).
- **Validar sua pasta:** `python tools/list_bgm_tracks.py --scan mods/music`.
