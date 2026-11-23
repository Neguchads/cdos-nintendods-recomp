// Standalone Windows GUI launcher for Castlevania: Dawn of Sorrow: Recompiled.
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
#include <shellapi.h>

#include <algorithm>
#include <cwctype>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

constexpr wchar_t kAppTitle[] = L"Castlevania: Dawn of Sorrow: Recompiled";
constexpr wchar_t kDefaultRomName[] = L"Castlevania - Dawn of Sorrow (USA).nds";

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

void write_stdout_utf8(const std::wstring& text) {
    HANDLE handle = GetStdHandle(STD_OUTPUT_HANDLE);
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

fs::path get_executable_dir() {
    std::wstring buf(32768, L'\0');
    DWORD len = GetModuleFileNameW(nullptr, buf.data(), static_cast<DWORD>(buf.size()));
    buf.resize(len);
    return fs::path(buf).parent_path();
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

void write_saved_rom_path(const fs::path& cache_file, const fs::path& rom_path) {
    std::error_code ec;
    fs::create_directories(cache_file.parent_path(), ec);
    std::ofstream out(cache_file, std::ios::binary | std::ios::trunc);
    if (!out) return;
    std::string utf8 = wide_to_utf8(rom_path.wstring());
    out.write(utf8.data(), static_cast<std::streamsize>(utf8.size()));
    out.put('\n');
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

fs::path find_rom_path(const fs::path& root, const fs::path& cli_rom, bool allow_prompt) {
    if (!cli_rom.empty()) {
        return cli_rom;
    }

    const std::vector<fs::path> candidates = {
        root / L"rom" / kDefaultRomName,
        root / kDefaultRomName,
        root.parent_path() / L"Roms" / kDefaultRomName,
    };
    for (const auto& candidate : candidates) {
        if (is_existing_file(candidate)) {
            return candidate;
        }
    }

    // Qualquer arquivo .nds na pasta rom/ local.
    std::error_code ec;
    fs::path rom_dir = root / L"rom";
    if (fs::is_directory(rom_dir, ec)) {
        for (const auto& entry : fs::directory_iterator(rom_dir, ec)) {
            if (entry.is_regular_file(ec) && has_nds_extension(entry.path())) {
                return entry.path();
            }
        }
    }

    fs::path cache_file = root / L"saves" / L"rom-path.txt";
    fs::path cached = read_saved_rom_path(cache_file);
    if (is_existing_file(cached)) {
        return cached;
    }

    if (!allow_prompt) {
        return {};
    }

    fs::path chosen = prompt_for_rom(root);
    if (is_existing_file(chosen)) {
        write_saved_rom_path(cache_file, chosen);
        return chosen;
    }
    return {};
}

}  // namespace

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    int argc = 0;
    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);

    bool print_command = false;
    fs::path cli_rom;
    std::vector<std::wstring> extra_args;

    for (int i = 1; i < argc; ++i) {
        std::wstring arg = argv[i];
        if (arg == L"--print-command") {
            print_command = true;
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

    const fs::path root = get_executable_dir();
    const fs::path runtime_dir = root / L"runtime";
    const fs::path runner_exe = runtime_dir / L"nds_runner.exe";
    const fs::path game_toml = root / L"game.toml";
    const fs::path ptbr_patch = root / L"mods" / L"ptbr" / L"dos-ptbr.dospatch";

    if (!is_existing_file(runner_exe)) {
        MessageBoxW(
            nullptr,
            L"runtime\\nds_runner.exe was not found.\n"
            L"Extract the full release archive or run: python tools\\build.py build\n\n"
            L"runtime\\nds_runner.exe nao encontrado.\n"
            L"Extraia o pacote completo ou rode: python tools\\build.py build",
            kAppTitle,
            MB_OK | MB_ICONERROR);
        return 1;
    }

    const fs::path rom_path = find_rom_path(root, cli_rom, !print_command);
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
        write_stdout_utf8(cmdline + L"\n");
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
