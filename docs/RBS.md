# Recomp Build System (RBS)

## Local Windows build
Keep the project in its own directory. The only private inputs are local; never commit or upload Roms/, generated/, analysis/, runtime/, saves/, run/, or toolchains/. No public PR may run on a personal self-hosted runner.

Use the existing Build-CDOS-Test.ps1 setup once (or prepare the same pinned frameworks manually): framework/ndsrecomp at e4a7f419 with the patch for the selected branch applied and ImGui v1.92.9b; framework/recomp-ui at f3f99a96; your USA ROM in Roms/Castlevania - Dawn of Sorrow (USA).nds. Do not reuse a framework patched for a different PR without rebuilding that dependency in a separate checkout. The existing setup script need not be rerun after each edit.

PowerShell:
- `./Build.ps1 -Profile Fast -Jobs 8`: Ninja incremental, content-based AOT phase cache, validate manifest.
- `./Build.ps1 -Profile Dev -Jobs 8`: incremental with debug symbols and Python/C++ tests.
- `./Build.ps1 -Profile Test -Jobs 8`: portable x86-64 compiler flags, unit tests, ROM smoke.
- `./Build.ps1 -Profile Release -Version v1.0.2-test.1 -Jobs 8`: tests, smoke, ZIP validation, SHA-256 and local build receipt.
- `./Build.ps1 -Profile Rebuild -Jobs 8`: force regeneration, clean compile, tests and smoke.

The same Ninja object tree is reused; switching profiles/CPU flags can cause a full recompilation. Cache phase keys include input contents, generator scripts, recompiler, and coverage/symbols. Missing or modified outputs invalidate the phase. This is phase-level invalidation, not per-overlay caching. A fresh checkout without the previous runtime coverage manifests may have lower AOT coverage. Do not claim identical performance or save compatibility until tested.

Optional local-only sccache: install a trusted official Windows binary, put it on PATH, set `$env:RBS_LOCAL_SCCACHE = '1'` before building. The wrapper selects a dedicated local cache and port. Do not configure remote cache backends for ROM-derived compilation. Without sccache, Ninja and AOT caching still work.

## Release flow
Release Please manages version/changelog PRs only; no empty stable release is created. Keep the existing v1.0.1 until the new build passes. Enable Settings > Actions > General > Allow GitHub Actions to create and approve pull requests if necessary; use manual CI rerun/dispatch for bot-created PRs, never auto-approve. Run version planning after a previous release has been published, to avoid stacked unpublished release PRs. Use Conventional Commits. Merge reviewed feature PRs and the version PR, then build the exact main commit. Stable versions must match .release-please-manifest.json.

After reviewing the ZIP, source, dependencies, licenses, and local test results:
```powershell
gh auth login
.\.venv\Scripts\python.exe tools/rbs_publish.py "dist/NAME-Windows-x64.zip" --confirm-draft
```
This explicitly creates a draft, not a published release. Check notes, tag, ZIP/checksum, and mark test versions pre-release. Publish manually. The receipt is local evidence, not a cryptographic attestation or malware scan. The binary is baseline x86-64 at the runner CMake flag level; test on other CPUs and clean Windows before a stable release.

For RecompLauncher verify the website version and actual asset after publishing. The external catalog cannot be forced from GitHub. Developer Hub/manual support may be needed.

## Quality and security limits
Public GitHub Actions run Python/manifest/clean-room checks and the synthetic RBS tests. The save contract verifies legacy paths and synthetic data separation; real save/savestate migration, Definitive profiles and randomizer tests need local runtime tests after feature integration. Do not distribute ROM/BIOS, personal saves, optional commercial video or derived source/cache. Review rights to distributed patches and compiled code separately. No public artifacts from untrusted builds. SBOM, vulnerability scanners, signing and branch rules are follow-up hardening, not claims of current security certification.

## Recommended branch governance
Require existing CI checks after they succeed on the infrastructure PR, require review, prohibit force pushes, use a maintainer-only release process. Configure in repository Settings > Rules > Rulesets. Never run public fork PRs on a personal runner.
