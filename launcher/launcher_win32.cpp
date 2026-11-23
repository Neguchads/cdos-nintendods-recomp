// Standalone Windows GUI launcher & 1-time installer for Castlevania: Dawn of Sorrow: Recompiled.
// Compilado com icone embutido (assets/recomplauncher/icon.ico) no final de tools/build.py.

#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <commdlg.h>
#include <knownfolders.h>
#include <objbase.h>
#include <shellapi.h>
#include <shlobj.h>
#include <shobjidl.h>

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cwctype>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

constexpr wchar_t kAppTitle[] = L"Castlevania: Dawn of Sorrow: Recompiled";
constexpr wchar_t kDefaultRomName[] = L"Castlevania - Dawn of Sorrow (USA).nds";
constexpr wchar_t kShortcutName[] = L"Castlevania - Dawn of Sorrow.lnk";
constexpr uint64_t kExpectedRomSize = 67108864ULL;
constexpr uint32_t kExpectedRomCrc32 = 0x135737f6U;

std::string wide_to_utf8(const std::wstring& input) {
    if (input.empty()) return {};
    int needed = WideCharToMultiByte(
        CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), nullptr, 0, nullptr, nullptr);
    if (needed <= 0) return {};
    std::string out(static_cast<size_t>(needed), '\0');
    WideCharToMultiByte(
        CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), out.data(), needed, nullptr, nullptr);
    return out;
}

std::wstring utf8_to_wide(const std::string& input) {
    if (input.empty()) return {};
    int needed = MultiByteToWideChar(
        CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), nullptr, 0);
    if (needed <= 0) return {};
    std::wstring out(static_cast<size_t>(needed), L'\0');
    MultiByteToWideChar(
        CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), out.data(), needed);
    return out;
}

void write_handle_utf8(DWORD std_handle_id, const std::wstring& text) {
    HANDLE handle = GetStdHandle(std_handle_id);
    if (handle == nullptr || handle == INVALID_HANDLE_VALUE) return;
    std::string bytes = wide_to_utf8(text);
    DWORD written = 0;
    WriteFile(handle, bytes.data(), static_cast<DWORD>(bytes.size()), &written, nullptr);
}

std::wstring quote_win32_arg(const std::wstring& arg) {
    if (!arg.empty() && arg.find_first_of(L" \t\n\v\"") == std::wstring::npos) {
        return arg;
    }
    std::wstring out;
    out.push_back(L'"');
    for (auto it = arg.begin();; ++it) {
        size_t backslashes = 0;
        while (it != arg.end() && *it == L'\\') {
            ++it;
            ++backslashes;
        }
        if (it == arg.end()) {
            out.append(backslashes * 2, L'\\');
            break;
        }
        if (*it == L'"') {
            out.append(backslashes * 2 + 1, L'\\');
            out.push_back(L'"');
        } else {
            out.append(backslashes, L'\\');
            out.push_back(*it);
        }
    }
    out.push_back(L'"');
    return out;
}

bool has_nds_extension(const fs::path& p) {
    std::wstring ext = p.extension().wstring();
    std::transform(ext.begin(), ext.end(), ext.begin(), [](wchar_t ch) {
        return static_cast<wchar_t>(std::towlower(ch));
    });
    return ext == L".nds";
}

bool is_existing_file(const fs::path& p) {
    std::error_code ec;
    return !p.empty() && fs::is_regular_file(p, ec);
}

fs::path get_executable_path() {
    std::wstring buf(32768, L'\0');
    DWORD len = GetModuleFileNameW(nullptr, buf.data(), static_cast<DWORD>(buf.size()));
    buf.resize(len);
    return fs::path(buf);
}

std::array<uint32_t, 256> make_crc32_table() {
    std::array<uint32_t, 256> table{};
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t c = i;
        for (int k = 0; k < 8; ++k) {
            c = (c & 1U) ? (0xEDB88320U ^ (c >> 1)) : (c >> 1);
        }
        table[i] = c;
    }
    return table;
}

bool validate_usa_rom(const fs::path& rom_path, std::wstring& err_out) {
    std::error_code ec;
    if (!fs::is_regular_file(rom_path, ec)) {
        err_out = L"ROM file not found / Arquivo ROM nao encontrado:\n" + rom_path.wstring();
        return false;
    }
    const uint64_t size = fs::file_size(rom_path, ec);
    if (ec || size != kExpectedRomSize) {
        err_out = L"Invalid ROM size. Expected 67,108,864 bytes (USA ACVE).\n"
                  L"Tamanho invalido. Esperado: 67.108.864 bytes (USA ACVE).";
        return false;
    }

    std::ifstream in(rom_path, std::ios::binary);
    if (!in) {
        err_out = L"Could not open ROM file for reading / Falha ao ler o arquivo ROM.";
        return false;
    }

    static const auto kTable = make_crc32_table();
    std::vector<uint8_t> buf(1U << 20);  // 1 MiB por bloco
    uint32_t crc = 0xFFFFFFFFU;
    bool checked_header = false;
    uint64_t total_read = 0;

    while (in) {
        in.read(reinterpret_cast<char*>(buf.data()), static_cast<std::streamsize>(buf.size()));
        const std::streamsize got = in.gcount();
        if (got <= 0) break;
        if (!checked_header) {
            if (got < 16 || std::memcmp(buf.data() + 0x0C, "ACVE", 4) != 0) {
                err_out = L"ROM game code is not ACVE (Castlevania: Dawn of Sorrow USA).\n"
                          L"Codigo da ROM nao e ACVE (Castlevania: Dawn of Sorrow USA).";
                return false;
            }
            checked_header = true;
        }
        for (std::streamsize i = 0; i < got; ++i) {
            crc = kTable[(crc ^ buf[static_cast<size_t>(i)]) & 0xFFU] ^ (crc >> 8);
        }
        total_read += static_cast<uint64_t>(got);
    }

    crc ^= 0xFFFFFFFFU;
    if (total_read != kExpectedRomSize || crc != kExpectedRomCrc32) {
        wchar_t hex_buf[32]{};
        std::swprintf(hex_buf, 32, L"%08x", crc);
        err_out = L"ROM CRC32 mismatch (got " + std::wstring(hex_buf) + L", expected 135737f6).\n"
                  L"CRC32 da ROM nao confere (esperado 135737f6 - USA ACVE).";
        return false;
    }
    return true;
}

bool install_rom_locally(const fs::path& src_rom, const fs::path& root, fs::path& installed_out, std::wstring& err_out) {
    const fs::path game_dir = root / L"game";
    const fs::path dst_rom = game_dir / kDefaultRomName;
    const fs::path tmp_rom = game_dir / L"dos-install.tmp";
    const fs::path setup_ok = game_dir / L"setup.ok";

    std::error_code ec;
    fs::create_directories(game_dir, ec);
    if (ec) {
        err_out = L"Could not create game\\ directory / Falha ao criar pasta game\\.";
        return false;
    }

    // Evita copiar sobre o mesmo arquivo se ja estiver em game/.
    if (!is_existing_file(dst_rom) || !fs::equivalent(src_rom, dst_rom, ec)) {
        ec.clear();
        fs::copy_file(src_rom, tmp_rom, fs::copy_options::overwrite_existing, ec);
        if (ec) {
            fs::remove(tmp_rom, ec);
            err_out = L"Failed to copy ROM into game\\ / Falha ao copiar ROM para game\\.";
            return false;
        }
        fs::rename(tmp_rom, dst_rom, ec);
        if (ec) {
            fs::remove(dst_rom, ec);
            ec.clear();
            fs::rename(tmp_rom, dst_rom, ec);
            if (ec) {
                fs::remove(tmp_rom, ec);
                err_out = L"Failed to finalize ROM install / Falha ao finalizar instalacao da ROM.";
                return false;
            }
        }
    }

    std::ofstream marker(setup_ok, std::ios::binary | std::ios::trunc);
    if (marker) {
        marker << "game_id=ACVE\n"
               << "size=67108864\n"
               << "crc32=135737f6\n"
               << "rom=Castlevania - Dawn of Sorrow (USA).nds\n";
    }
    installed_out = dst_rom;
    return true;
}

fs::path get_desktop_dir() {
    PWSTR raw_path = nullptr;
    if (SUCCEEDED(SHGetKnownFolderPath(FOLDERID_Desktop, 0, nullptr, &raw_path)) && raw_path != nullptr) {
        fs::path result(raw_path);
        CoTaskMemFree(raw_path);
        return result;
    }
    return {};
}

bool create_shortcut_lnk(const fs::path& lnk_path, const fs::path& target_exe, const fs::path& working_dir) {
    std::error_code ec;
    if (!lnk_path.parent_path().empty()) {
        fs::create_directories(lnk_path.parent_path(), ec);
    }

    HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    const bool need_uninit = SUCCEEDED(hr);
    if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) {
        return false;
    }

    bool created = false;
    IShellLinkW* shell_link = nullptr;
    hr = CoCreateInstance(
        CLSID_ShellLink, nullptr, CLSCTX_INPROC_SERVER, IID_IShellLinkW, reinterpret_cast<void**>(&shell_link));
    if (SUCCEEDED(hr) && shell_link != nullptr) {
        shell_link->SetPath(target_exe.c_str());
        shell_link->SetWorkingDirectory(working_dir.c_str());
        shell_link->SetDescription(kAppTitle);
        shell_link->SetIconLocation(target_exe.c_str(), 0);

        IPersistFile* persist_file = nullptr;
        hr = shell_link->QueryInterface(IID_IPersistFile, reinterpret_cast<void**>(&persist_file));
        if (SUCCEEDED(hr) && persist_file != nullptr) {
            hr = persist_file->Save(lnk_path.c_str(), TRUE);
            created = SUCCEEDED(hr);
            persist_file->Release();
        }
        shell_link->Release();
    }

    if (need_uninit) {
        CoUninitialize();
    }
    return created;
}

fs::path read_saved_rom_path(const fs::path& cache_file) {
    std::ifstream in(cache_file, std::ios::binary);
    if (!in) return {};
    std::string line;
    std::getline(in, line);
    while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) {
        line.pop_back();
    }
    if (line.empty()) return {};
    return fs::path(utf8_to_wide(line));
}

fs::path prompt_for_rom(const fs::path& initial_dir) {
    std::wstring file_buf(32768, L'\0');
    std::wstring init_dir = initial_dir.wstring();

    OPENFILENAMEW ofn{};
    ofn.lStructSize = sizeof(ofn);
    ofn.lpstrFilter = L"Nintendo DS ROM (*.nds)\0*.nds\0All Files (*.*)\0*.*\0";
    ofn.lpstrFile = file_buf.data();
    ofn.nMaxFile = static_cast<DWORD>(file_buf.size());
    ofn.lpstrInitialDir = init_dir.c_str();
    ofn.lpstrTitle = L"Select Castlevania: Dawn of Sorrow (USA) .nds ROM";
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_HIDEREADONLY;

    if (!GetOpenFileNameW(&ofn)) {
        return {};
    }
    return fs::path(file_buf.c_str());
}

fs::path find_existing_rom(const fs::path& root, const fs::path& cli_rom) {
    if (!cli_rom.empty()) {
        return cli_rom;
    }

    const std::vector<fs::path> candidates = {
        root / L"game" / kDefaultRomName,
        root / L"rom" / kDefaultRomName,
        root / kDefaultRomName,
        root.parent_path() / L"Roms" / kDefaultRomName,
    };
    for (const auto& candidate : candidates) {
        if (is_existing_file(candidate)) {
            return candidate;
        }
    }

    std::error_code ec;
    for (const wchar_t* sub : {L"game", L"rom"}) {
        fs::path dir = root / sub;
        if (fs::is_directory(dir, ec)) {
            for (const auto& entry : fs::directory_iterator(dir, ec)) {
                if (entry.is_regular_file(ec) && has_nds_extension(entry.path())) {
                    return entry.path();
                }
            }
        }
    }

    fs::path cached = read_saved_rom_path(root / L"saves" / L"rom-path.txt");
    if (is_existing_file(cached)) {
        return cached;
    }
    return {};
}

}  // namespace

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    int argc = 0;
    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);

    bool print_command = false;
    bool setup_only = false;
    bool create_desktop_shortcut = false;
    fs::path cli_rom;
    fs::path explicit_shortcut_path;
    std::vector<std::wstring> extra_args;

    for (int i = 1; i < argc; ++i) {
        std::wstring arg = argv[i];
        if (arg == L"--print-command") {
            print_command = true;
        } else if (arg == L"--setup-only") {
            setup_only = true;
        } else if (arg == L"--create-shortcut") {
            create_desktop_shortcut = true;
        } else if (arg == L"--shortcut-path" && i + 1 < argc) {
            explicit_shortcut_path = fs::path(argv[++i]);
        } else if (arg == L"--rom" && i + 1 < argc) {
            cli_rom = fs::path(argv[++i]);
        } else if (cli_rom.empty() && !arg.empty() && arg[0] != L'-' && has_nds_extension(arg)) {
            cli_rom = fs::path(arg);
        } else {
            extra_args.push_back(arg);
        }
    }
    if (argv != nullptr) {
        LocalFree(argv);
    }

    const fs::path exe_path = get_executable_path();
    const fs::path root = exe_path.parent_path();
    const fs::path runtime_dir = root / L"runtime";
    const fs::path runner_exe = runtime_dir / L"nds_runner.exe";
    const fs::path game_toml = root / L"game.toml";
    const fs::path ptbr_patch = root / L"mods" / L"ptbr" / L"dos-ptbr.dospatch";
    const fs::path def_en_patch = root / L"mods" / L"definitive" / L"dos-definitive-en.dospatch";
    const fs::path def_ptbr_patch = root / L"mods" / L"definitive" / L"dos-definitive-ptbr.dospatch";
    const fs::path intro_video = root / L"mods" / L"intro" / L"opening.mp4";
    const fs::path mod_registry = root / L"mods" / L"registry.json";
    const fs::path mod_data_dir = root / L"mods";

    if (!is_existing_file(runner_exe)) {
        const std::wstring msg =
            L"runtime\\nds_runner.exe was not found.\n"
            L"Extract the full release archive or run: python tools\\build.py build\n\n"
            L"runtime\\nds_runner.exe nao encontrado.\n"
            L"Extraia o pacote completo ou rode: python tools\\build.py build";
        if (setup_only || print_command) {
            write_handle_utf8(STD_ERROR_HANDLE, msg + L"\n");
        } else {
            MessageBoxW(nullptr, msg.c_str(), kAppTitle, MB_OK | MB_ICONERROR);
        }
        return 1;
    }

    if (setup_only) {
        fs::path src_rom = cli_rom.empty() ? prompt_for_rom(root) : cli_rom;
        std::wstring err;
        if (src_rom.empty() || !validate_usa_rom(src_rom, err)) {
            write_handle_utf8(STD_ERROR_HANDLE, (err.empty() ? L"No ROM selected." : err) + L"\n");
            return 2;
        }
        fs::path installed_rom;
        if (!install_rom_locally(src_rom, root, installed_rom, err)) {
            write_handle_utf8(STD_ERROR_HANDLE, err + L"\n");
            return 2;
        }
        if (!explicit_shortcut_path.empty()) {
            if (!create_shortcut_lnk(explicit_shortcut_path, exe_path, root)) {
                write_handle_utf8(STD_ERROR_HANDLE, L"Failed to create shortcut.\n");
                return 2;
            }
        } else if (create_desktop_shortcut) {
            fs::path desktop = get_desktop_dir();
            if (desktop.empty() || !create_shortcut_lnk(desktop / kShortcutName, exe_path, root)) {
                write_handle_utf8(STD_ERROR_HANDLE, L"Failed to create Desktop shortcut.\n");
                return 2;
            }
        }
        write_handle_utf8(STD_OUTPUT_HANDLE, L"OK: " + installed_rom.wstring() + L"\n");
        return 0;
    }

    fs::path rom_path = find_existing_rom(root, cli_rom);
    if (rom_path.empty() && !print_command) {
        fs::path chosen = prompt_for_rom(root);
        if (chosen.empty()) {
            return 1;
        }
        std::wstring err;
        if (!validate_usa_rom(chosen, err)) {
            MessageBoxW(nullptr, err.c_str(), kAppTitle, MB_OK | MB_ICONERROR);
            return 1;
        }
        if (!install_rom_locally(chosen, root, rom_path, err)) {
            MessageBoxW(nullptr, err.c_str(), kAppTitle, MB_OK | MB_ICONERROR);
            return 1;
        }
        fs::path desktop = get_desktop_dir();
        if (!desktop.empty()) {
            int answer = MessageBoxW(
                nullptr,
                L"ROM verified and installed locally in game\\!\n"
                L"Create a Desktop shortcut for Castlevania: Dawn of Sorrow?\n\n"
                L"ROM verificada e instalada em game\\!\n"
                L"Criar atalho na Area de Trabalho para Castlevania: Dawn of Sorrow?",
                kAppTitle,
                MB_YESNO | MB_ICONQUESTION);
            if (answer == IDYES) {
                create_shortcut_lnk(desktop / kShortcutName, exe_path, root);
            }
        }
    }

    if (rom_path.empty() || !is_existing_file(rom_path)) {
        if (!print_command && !cli_rom.empty()) {
            std::wstring msg = L"ROM file not found / ROM nao encontrada:\n" + cli_rom.wstring();
            MessageBoxW(nullptr, msg.c_str(), kAppTitle, MB_OK | MB_ICONERROR);
        }
        return 1;
    }

    const fs::path bios_dir = root / L"run" / L"bios";
    const fs::path savestates_dir = root / L"run" / L"savestates";
    const fs::path saves_dir = root / L"saves";

    if (!print_command) {
        std::error_code ec;
        fs::create_directories(bios_dir, ec);
        fs::create_directories(savestates_dir, ec);
        fs::create_directories(saves_dir, ec);
    }

    std::vector<std::wstring> cmd_args;
    cmd_args.push_back(runner_exe.wstring());
    cmd_args.push_back(bios_dir.wstring());
    cmd_args.push_back(L"--interactive");
    cmd_args.push_back(L"--rom");
    cmd_args.push_back(rom_path.wstring());
    if (is_existing_file(ptbr_patch)) {
        cmd_args.push_back(L"--ptbr-patch");
        cmd_args.push_back(ptbr_patch.wstring());
    }
    if (is_existing_file(def_en_patch)) {
        cmd_args.push_back(L"--definitive-en-patch");
        cmd_args.push_back(def_en_patch.wstring());
    }
    if (is_existing_file(def_ptbr_patch)) {
        cmd_args.push_back(L"--definitive-ptbr-patch");
        cmd_args.push_back(def_ptbr_patch.wstring());
    }
    if (is_existing_file(intro_video)) {
        cmd_args.push_back(L"--intro-video");
        cmd_args.push_back(intro_video.wstring());
    }
    if (is_existing_file(mod_registry)) {
        cmd_args.push_back(L"--mod-registry");
        cmd_args.push_back(mod_registry.wstring());
        cmd_args.push_back(L"--mod-data-dir");
        cmd_args.push_back(mod_data_dir.wstring());
    }
    cmd_args.push_back(L"--config");
    cmd_args.push_back(game_toml.wstring());
    cmd_args.push_back(L"--freebios");
    cmd_args.push_back(L"--generated-firmware");
    cmd_args.push_back(L"--boot");
    cmd_args.push_back(L"direct");
    cmd_args.push_back(L"--startup-mode");
    cmd_args.push_back(L"automatic");
    cmd_args.push_back(L"--diagnostics");
    cmd_args.push_back(L"off");
    cmd_args.push_back(L"--no-coverage-manifest");
    cmd_args.push_back(L"--runtime-settings-path");
    cmd_args.push_back((saves_dir / L"dos-settings.ini").wstring());
    cmd_args.push_back(L"--savestate-dir");
    cmd_args.push_back(savestates_dir.wstring());
    cmd_args.push_back(L"--save-path");
    cmd_args.push_back((saves_dir / L"dos.sav").wstring());
    cmd_args.push_back(L"--firmware-state-path");
    cmd_args.push_back((root / L"run" / L"firmware_state.bin").wstring());
    for (const auto& extra : extra_args) {
        cmd_args.push_back(extra);
    }

    std::wstring cmdline;
    for (size_t i = 0; i < cmd_args.size(); ++i) {
        if (i > 0) cmdline.push_back(L' ');
        cmdline += quote_win32_arg(cmd_args[i]);
    }

    if (print_command) {
        write_handle_utf8(STD_OUTPUT_HANDLE, cmdline + L"\n");
        return 0;
    }

    SetEnvironmentVariableW(L"NDS_HOSTPROF", L"off");

    STARTUPINFOW si{};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};
    std::wstring mutable_cmd = cmdline;
    std::wstring runtime_cwd = runtime_dir.wstring();

    BOOL ok = CreateProcessW(
        runner_exe.c_str(),
        mutable_cmd.data(),
        nullptr,
        nullptr,
        FALSE,
        0,
        nullptr,
        runtime_cwd.c_str(),
        &si,
        &pi);
    if (!ok) {
        MessageBoxW(
            nullptr,
            L"Failed to start runtime\\nds_runner.exe.\n"
            L"Falha ao iniciar runtime\\nds_runner.exe.",
            kAppTitle,
            MB_OK | MB_ICONERROR);
        return 1;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD exit_code = 0;
    GetExitCodeProcess(pi.hProcess, &exit_code);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return static_cast<int>(exit_code);
}
