# CHAD Feature Assurance — maintenance and quality policy

This is a reference implementation for Dawn of Sorrow; extraction into Chad Recomp is a future task, not a dependency. No game code, packaging, save formats or third-party assets are changed.

## Source of truth

Edit `quality/features.json` after reviewing a requirement. Each entry has a stable ID, a source, an optional issue, an acceptance criterion and a list of evidence references. Keep the scope and baseline explicit. Use the same status vocabulary across roadmap and issues. Do not mark planned work complete just because an issue closes or a build succeeds. Record platform, commit, test procedure, result and limitations in evidence links before making verification claims. Existing README verification claims are represented as documentary evidence only; no new gameplay runs were executed for this initial inventory.

## Metrics and generated outputs

Run `node tools/quality/generate-dashboard.mjs` from the repository root; run `node tools/quality/generate-dashboard.mjs --check` in CI. No package installation or external service is required. The generator rejects duplicate IDs, unknown statuses and missing source files and checks deterministic SVG, Markdown and JSON output. The schema is a companion machine-readable contract; the generator performs its own dependency-free structural checks rather than full JSON Schema evaluation.

The numerator counts documented verified, implemented and beta requirements; the denominator includes every catalogued requirement. Partial and unknown are excluded from the numerator. These metrics are not effort estimates, test pass rates, coverage of all game behavior or release readiness. A changing catalog can change the percentage without code changes. Evidence coverage measures references recorded, not their validity; maintainers must review evidence. Never infer runtime success from compilation alone.

## Platform matrix (initial documentary assessment)

| Area | Windows | Linux / Steam Deck | Android |
|---|---|---|---|
| Core and rendering | Documented verified | Runtime unverified | Runtime unverified |
| Custom music and mods | Documented verified | Unverified | Unverified |
| Native Direct3D 12 | Documented verified | Not applicable | Not applicable |
| Build tooling | Documented functional | Script present | Gradle/NDK skeleton |
| Dual-screen physical devices | Not applicable | Not assessed | Planned (#52) |

See [MULTIPLATFORM.md](MULTIPLATFORM.md) for constraints. Future improvements: per-platform evidence registry, weighted acceptance criteria with explicit rationale, automated CI artifact ingestion, benchmark trends and regression gates, HTML portal, and shared Chad Recomp distribution. Keep optional enhancements distinct from issue acceptance criteria; do not close #38 on the basis of this dashboard.

## Maintenance checklist

- Update registry and evidence when a feature, limitation or test result changes.
- Generate outputs and review the diff alongside the related implementation PR.
- Run the existing repository tests and the dashboard consistency check.
- Keep the original roadmap, changelog and release notes as historical records; link the generated inventory instead of manually duplicating percentages.
- Record game/runtime test evidence separately; review regressions and platform-specific limits before release.

## Dashboard presentation

The dashboard uses neutral, ChatGPT-inspired metric cards and subtle progress bars, with separate light and dark SVG assets selected via GitHub-supported `picture` markup. The README shows the summary and a collapsible subsystem grid; the full audit shows both. These are static generated images, not interactive widgets; the registry remains the source of truth.
