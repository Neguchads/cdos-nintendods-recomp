# Notas de Sessão (Fatia 2 — Composição Modular Empilhável de Patches & Refresh da Homepage)

## Feito
- **Composição Modular Empilhável (Fatia 2, inspirada no `cdos-patcher-tool` e `@leomontenegro6`):**
  - `mods/registry.json` separado em `"addons"` combináveis (**Tradução PT-BR v1.1**, **Dawn of Dignity**, **No Magic Seals**, **Fixed Luck**, **Voice Restore Project**) e `"campaigns"` exclusivas.
  - Merger 3-way byte-diff em memória sobre a `base_rom` USA limpa + recálculo automático do CRC-16/MODBUS do cabeçalho NDS (`0x15E..0x15F`) em `dos_mod_registry.cpp`, checkboxes em `F1 -> Mods & Campanhas`, persistência `dos_active_addons` em INI, saves isolados por combinação (`modular-stack`) e paridade em `tools/mod_resolver.py` + testes C++/Python.
- **Homepage (`README.md`) atualizada** em Inglês e Português (BR) com resumo visual de destaques e tabelas de status atualizadas.

## Falta / Próximos passos
- Avaliar publicação de nova release (`v1.2.3` ou `v1.3.0`) com a Fatia 2 empacotada.
- Próximos épicos de roadmap: `#36` (HD Texture Packs), `#37` (Cheat Manager), `#38` (Advanced Music Manager) e `#40` (EUR Multi-language).
