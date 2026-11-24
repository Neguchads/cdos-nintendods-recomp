#!/usr/bin/env python3
"""Assistente visual para configurar musicas customizadas (.mp3/.wav/.ogg) em Castlevania: Dawn of Sorrow.

Rode dando duplo clique em Configurar_Musica.bat (ou: python mods/music/configurar_musica.py).
Fluxo:
  1. Abre a janela do Windows Explorer para escolher uma ou mais musicas (.mp3, .wav, .ogg).
  2. Copia os arquivos para esta pasta mods/music/ (se vierem de outra pasta do PC).
  3. Pergunta se voce quer substituir um estagio/area especifica (#00..#29) OU ativar o Modo Jukebox /
     Playlist Global (muta TODAS as 30 BGMs do DS e toca apenas as musicas selecionadas, mantendo SFX).
  4. Salva atomicamente em mods/music/music.json.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

SUPPORTED_EXTS = {".wav", ".mp3", ".ogg"}

BGM_TRACKS: list[tuple[int, str, str]] = [
    (0, "SDL_BGM_ARR1_", "Vampire Killer (Arranged)"),
    (1, "SDL_BGM_ARR2_", "Bloody Tears (Arranged)"),
    (2, "SDL_BGM_BOSS1_", "Into the Dark Night (Boss 1)"),
    (3, "SDL_BGM_BOSS2_", "Evil Invitation (Boss 2)"),
    (4, "SDL_BGM_ENDING_", "Ending Theme"),
    (5, "SDL_BGM_EV_BOSS_", "Event Boss / Tension"),
    (6, "SDL_BGM_L2_BOSS_", "Final Boss (Menace)"),
    (7, "SDL_BGM_NAME_", "Name Entry / File Select (Tela de Save)"),
    (8, "SDS_BGM_OVER_", "Game Over"),
    (9, "SDL_BGM_PRE_", "Prelude / Prologue"),
    (10, "SDL_BGM_SHOP_", "Hammer's Shop (Loja do Hammer)"),
    (11, "SDL_BGM_ST00_1_", "Pitch Black Intrusion (Lost Village / 1a Fase)"),
    (12, "SDL_BGM_ST00_2_", "Lost Village (Interior)"),
    (13, "SDL_BGM_ST01_", "Dracula's Tears (Wizardry Lab)"),
    (14, "SDL_BGM_ST02_", "Garden of Madness"),
    (15, "SDL_BGM_ST03_", "Dark Chapel"),
    (16, "SDL_BGM_ST04_", "Demon Guest House"),
    (17, "SDL_BGM_ST05_", "Condemned Tower"),
    (18, "SDL_BGM_ST06_", "Subterranean Hell"),
    (19, "SDL_BGM_ST07_", "Silenced Ruins"),
    (20, "SDL_BGM_ST08_", "Cursed Clock Tower"),
    (21, "SDL_BGM_ST09_", "The Pinnacle"),
    (22, "SDL_BGM_ST10_", "Mine of Judgment"),
    (23, "SDL_BGM_ST11_", "The Abyss"),
    (24, "SDL_BGM_ST12_", "Abyss Depths / Extra"),
    (25, "SDS_BGM_STAFF_", "Credits / Staff Roll"),
    (26, "SDL_BGM_TR_BOSS1_", "Scarlet Battle Soul (Boss 3)"),
    (27, "SDL_BGM_TR_BOSS2_", "Last Battle / Death & Julius"),
    (28, "SDL_BGM_WIND_", "Wind Ambience"),
    (29, "SDL_BGM_YOKO_", "Yoko's Soul Synthesis"),
]


def load_manifest(music_dir: Path) -> dict[str, object]:
    """Carrega music.json existente preservando configuracoes previas."""
    manifest_path = music_dir / "music.json"
    default_data: dict[str, object] = {
        "jukebox": {"enabled": False, "shuffle": False, "playlist": []},
        "tracks": {},
    }
    if not manifest_path.is_file():
        return default_data
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default_data
    if not isinstance(raw, dict):
        return default_data
    jb = raw.get("jukebox")
    if not isinstance(jb, dict):
        jb = {"enabled": False, "shuffle": False, "playlist": []}
    tracks = raw.get("tracks")
    if not isinstance(tracks, dict):
        tracks = {}
    return {
        "jukebox": {
            "enabled": bool(jb.get("enabled", False)),
            "shuffle": bool(jb.get("shuffle", False)),
            "playlist": [str(x) for x in jb.get("playlist", []) if isinstance(x, str)],
        },
        "tracks": dict(tracks),
    }


def save_manifest_atomic(music_dir: Path, data: dict[str, object]) -> Path:
    """Escreve music.json de forma atomica (tmp + os.replace)."""
    music_dir.mkdir(parents=True, exist_ok=True)
    dst = music_dir / "music.json"
    tmp = music_dir / "music.json.tmp"
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, dst)
    return dst


def import_audio_file_to_music_dir(src_path: Path, music_dir: Path) -> str:
    """Garante que o arquivo de audio esteja dentro de music_dir, retornando seu nome relativo."""
    src = src_path.resolve()
    if not src.is_file():
        raise FileNotFoundError(f"Arquivo nao encontrado: {src}")
    ext = src.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Formato nao suportado ({ext}). Use .mp3, .wav ou .ogg.")

    music_dir_resolved = music_dir.resolve()
    music_dir_resolved.mkdir(parents=True, exist_ok=True)

    # Ja esta na raiz da pasta mods/music/ -> usa direto sem copiar
    if src.parent == music_dir_resolved:
        return src.name

    safe_name = src.name.replace("/", "_").replace("\\", "_").replace(":", "_")
    dst = music_dir_resolved / safe_name
    if dst.exists() and dst.stat().st_size != src.stat().st_size:
        stem = dst.stem
        idx = 2
        while dst.exists():
            dst = music_dir_resolved / f"{stem}_{idx}{ext}"
            idx += 1
    if not dst.exists():
        shutil.copy2(src, dst)
    return dst.name


def assign_track_in_manifest(
    music_dir: Path,
    track_id: int,
    filename: str,
    *,
    loop: bool = True,
    gain_db: float = 0.0,
) -> Path:
    """Vincula uma faixa especifica (00..29) a um arquivo em music.json."""
    if not (0 <= track_id < len(BGM_TRACKS)):
        raise ValueError(f"track_id invalido: {track_id}")
    data = load_manifest(music_dir)
    tracks = data["tracks"]
    assert isinstance(tracks, dict)
    key = f"{track_id:02d}"
    tracks[key] = {
        "file": filename,
        "loop": bool(loop),
        "loop_start_ms": -1,
        "loop_end_ms": -1,
        "gain_db": round(float(gain_db), 2),
    }
    return save_manifest_atomic(music_dir, data)


def configure_jukebox_in_manifest(
    music_dir: Path,
    filenames: list[str],
    *,
    enabled: bool = True,
    shuffle: bool = False,
    append: bool = False,
) -> Path:
    """Configura o Modo Jukebox / Playlist Global em music.json."""
    data = load_manifest(music_dir)
    jb = data["jukebox"]
    assert isinstance(jb, dict)
    playlist: list[str] = list(jb.get("playlist", [])) if append else []
    for name in filenames:
        if name and name not in playlist:
            playlist.append(name)
    jb["enabled"] = bool(enabled and playlist)
    jb["shuffle"] = bool(shuffle)
    jb["playlist"] = playlist
    return save_manifest_atomic(music_dir, data)


def run_gui(music_dir: Path) -> int:
    """Interface grafica simples usando Windows Explorer (filedialog) + seletor de estagio/jukebox."""
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.withdraw()

    picked = filedialog.askopenfilenames(
        title="Escolha uma ou mais musicas (.mp3, .wav, .ogg) - Castlevania: Dawn of Sorrow",
        initialdir=str(music_dir),
        filetypes=[
            ("Arquivos de Audio", "*.mp3 *.wav *.ogg"),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),
            ("OGG Vorbis", "*.ogg"),
        ],
    )
    if not picked:
        root.destroy()
        return 0

    imported_names: list[str] = []
    for raw_path in picked:
        try:
            imported_names.append(import_audio_file_to_music_dir(Path(raw_path), music_dir))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro ao importar musica", f"{raw_path}\n\n{exc}")
            root.destroy()
            return 1

    root.deiconify()
    root.title("Configurar Musica - Castlevania: Dawn of Sorrow Recomp")
    root.geometry("620x540")
    root.configure(bg="#15141c")

    fg = "#eee8f5"
    accent = "#c6923a"
    panel = "#1e1c28"

    tk.Label(
        root,
        text="Castlevania: Dawn of Sorrow — Configurador de Musica",
        font=("Segoe UI", 13, "bold"),
        bg="#15141c",
        fg=accent,
    ).pack(pady=(12, 4))

    files_summary = (
        imported_names[0]
        if len(imported_names) == 1
        else f"{len(imported_names)} musicas selecionadas ({', '.join(imported_names[:3])}{'...' if len(imported_names) > 3 else ''})"
    )
    tk.Label(
        root,
        text=f"Selecionado: {files_summary}",
        font=("Segoe UI", 10),
        bg="#15141c",
        fg=fg,
        wraplength=580,
    ).pack(pady=(0, 10))

    mode_var = tk.StringVar(value="jukebox" if len(imported_names) > 1 else "stage")

    mode_frame = tk.Frame(root, bg=panel, padx=10, pady=8)
    mode_frame.pack(fill="x", padx=16, pady=(0, 8))

    tk.Radiobutton(
        mode_frame,
        text="Substituir 1 estagio / area especifica do jogo (30 faixas)",
        variable=mode_var,
        value="stage",
        bg=panel,
        fg=fg,
        selectcolor="#2b273a",
        activebackground=panel,
        activeforeground=fg,
        font=("Segoe UI", 10, "bold"),
        state=("disabled" if len(imported_names) > 1 else "normal"),
    ).pack(anchor="w")

    tk.Radiobutton(
        mode_frame,
        text="Modo Jukebox / Playlist Global (muta TODAS as BGMs do DS e toca so estas)",
        variable=mode_var,
        value="jukebox",
        bg=panel,
        fg=fg,
        selectcolor="#2b273a",
        activebackground=panel,
        activeforeground=fg,
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor="w", pady=(4, 0))

    # Lista dos 30 estagios
    stage_frame = tk.Frame(root, bg="#15141c")
    stage_frame.pack(fill="both", expand=True, padx=16, pady=4)

    tk.Label(
        stage_frame,
        text="Escolha o estagio / musica do jogo para substituir:",
        bg="#15141c",
        fg=fg,
        font=("Segoe UI", 9),
    ).pack(anchor="w")

    list_container = tk.Frame(stage_frame, bg="#15141c")
    list_container.pack(fill="both", expand=True, pady=(4, 6))

    scrollbar = ttk.Scrollbar(list_container, orient="vertical")
    listbox = tk.Listbox(
        list_container,
        yscrollcommand=scrollbar.set,
        bg="#201e2b",
        fg=fg,
        selectbackground="#6e2c3e",
        selectforeground="#ffffff",
        font=("Consolas", 10),
        activestyle="none",
        height=13,
    )
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)

    for tid, sdat, label in BGM_TRACKS:
        listbox.insert(tk.END, f"#{tid:02d}  {label}  ({sdat})")
    listbox.selection_set(11)  # Default: #11 Pitch Black Intrusion
    listbox.see(11)

    opts_frame = tk.Frame(root, bg=panel, padx=10, pady=8)
    opts_frame.pack(fill="x", padx=16, pady=(2, 8))

    loop_var = tk.BooleanVar(value=True)
    shuffle_var = tk.BooleanVar(value=False)
    append_var = tk.BooleanVar(value=True)

    tk.Checkbutton(
        opts_frame,
        text="Loop continuo (estagio)",
        variable=loop_var,
        bg=panel,
        fg=fg,
        selectcolor="#2b273a",
        activebackground=panel,
        activeforeground=fg,
    ).grid(row=0, column=0, sticky="w", padx=(0, 14))

    tk.Checkbutton(
        opts_frame,
        text="Jukebox: Ordem Aleatoria (Shuffle)",
        variable=shuffle_var,
        bg=panel,
        fg=fg,
        selectcolor="#2b273a",
        activebackground=panel,
        activeforeground=fg,
    ).grid(row=0, column=1, sticky="w", padx=(0, 14))

    tk.Checkbutton(
        opts_frame,
        text="Jukebox: Adicionar a playlist atual",
        variable=append_var,
        bg=panel,
        fg=fg,
        selectcolor="#2b273a",
        activebackground=panel,
        activeforeground=fg,
    ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

    result_code = {"rc": 0}

    def on_ok() -> None:
        if mode_var.get() == "jukebox":
            save_path = configure_jukebox_in_manifest(
                music_dir,
                imported_names,
                enabled=True,
                shuffle=shuffle_var.get(),
                append=append_var.get(),
            )
            msg = (
                f"Modo Jukebox / Playlist Global ativado!\n\n"
                f"Musicas adicionadas: {len(imported_names)}\n"
                f"Salvo em: {save_path}\n\n"
                f"Todas as BGMs originais do DS serao mutadas (SFX mantido).\n"
                f"Se o jogo ja estiver aberto, aperte F1 -> Audio -> Reescanear Pasta mods/music."
            )
        else:
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Escolha um estagio", "Selecione uma das 30 faixas na lista.")
                return
            tid = int(sel[0])
            save_path = assign_track_in_manifest(
                music_dir,
                tid,
                imported_names[0],
                loop=loop_var.get(),
            )
            _, _, stage_label = BGM_TRACKS[tid]
            msg = (
                f"Musica configurada com sucesso!\n\n"
                f"Estagio: #{tid:02d} {stage_label}\n"
                f"Arquivo: {imported_names[0]}\n"
                f"Salvo em: {save_path}\n\n"
                f"Se o jogo ja estiver aberto, aperte F1 -> Audio -> Reescanear Pasta mods/music."
            )
        messagebox.showinfo("Pronto!", msg)
        root.destroy()

    btn_frame = tk.Frame(root, bg="#15141c")
    btn_frame.pack(fill="x", padx=16, pady=(0, 12))

    tk.Button(
        btn_frame,
        text="OK — Salvar e Configurar",
        command=on_ok,
        bg="#7b2d43",
        fg="#ffffff",
        activebackground="#963954",
        activeforeground="#ffffff",
        font=("Segoe UI", 10, "bold"),
        padx=18,
        pady=6,
        relief="flat",
        cursor="hand2",
    ).pack(side="right")

    tk.Button(
        btn_frame,
        text="Cancelar",
        command=root.destroy,
        bg="#2d2a3b",
        fg=fg,
        activebackground="#3c384e",
        activeforeground=fg,
        font=("Segoe UI", 10),
        padx=14,
        pady=6,
        relief="flat",
        cursor="hand2",
    ).pack(side="right", padx=(0, 8))

    root.mainloop()
    return result_code["rc"]


def main(argv: list[str] | None = None) -> int:
    music_dir = Path(__file__).resolve().parent
    args = list(sys.argv[1:] if argv is None else argv)
    if "--dir" in args:
        idx = args.index("--dir")
        if idx + 1 < len(args):
            music_dir = Path(args[idx + 1]).resolve()
    return run_gui(music_dir)


if __name__ == "__main__":
    raise SystemExit(main())
