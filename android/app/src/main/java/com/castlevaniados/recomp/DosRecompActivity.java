package com.castlevaniados.recomp;

import java.io.File;
import org.libsdl.app.SDLActivity;

public class DosRecompActivity extends SDLActivity {
    @Override
    protected String[] getLibraries() {
        return new String[] {
            "SDL3",
            "main"
        };
    }

    @Override
    protected String[] getArguments() {
        File extDir = getExternalFilesDir(null);
        String base = extDir != null ? extDir.getAbsolutePath() : getFilesDir().getAbsolutePath();
        return new String[] {
            base + "/bios",
            "--interactive",
            "--rom", base + "/rom/castlevania_dos_usa.nds",
            "--ptbr-patch", base + "/mods/ptbr/dos-ptbr.dospatch",
            "--config", base + "/game.toml",
            "--freebios",
            "--generated-firmware",
            "--boot", "direct",
            "--startup-mode", "automatic",
            "--diagnostics", "off",
            "--no-coverage-manifest",
            "--runtime-settings-path", base + "/saves/dos-settings.ini",
            "--savestate-dir", base + "/savestates",
            "--save-path", base + "/saves/dos.sav",
            "--firmware-state-path", base + "/firmware_state.bin"
        };
    }
}
