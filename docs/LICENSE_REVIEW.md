# Licenciamento e proveniência — revisão 2026-11-24

## Decisão

Não há uma licença MIT global para este projeto. Ele integra código de origens diferentes, inclusive componentes com condições não comerciais e copyleft. Uma eventual licença de código original não autoriza a distribuição do jogo, assets, patches de terceiros ou um runner sob MIT.

A licença MIT em [`.github/advanced/LICENSE`](../.github/advanced/LICENSE) é **restrita a `.github/advanced/fuzz.py` e `.github/advanced/benchmark.py`**, scripts sintéticos originais de CI criados especificamente para este projeto. Dependências e módulos importados conservam seus próprios termos. Não se estende a outros arquivos.

## Dependências verificadas nas revisões efetivamente fixadas pelo RBS

| Componente | Revisão | Termos constatados |
| --- | --- | --- |
| RetroPortingToolKit/ndsrecomp | e4a7f419 | PolyForm Noncommercial 1.0.0 como padrão; exceções MIT e GPL-3.0-or-later |
| ndsrecomp runner/oracle | e4a7f419 | Código próprio de certos diretórios MIT; componentes derivados de melonDS GPL-3.0-or-later. O upstream classifica os binários combinados nds_runner e ndsref como GPL-3.0-or-later. |
| RetroPortingToolKit/recomp-ui | f3f99a96 | MIT, preservando copyright e aviso da licença |
| SDL3, Dear ImGui, LLVM/MinGW, dsd, FreeBIOS e demais dependências | versões do RBS e toolchain | Verificar termos e notices de cada versão efetivamente redistribuída; não herdam a licença do port. |

Fontes primárias:
- [ndsrecomp LICENSE (commit e4a7f419)](https://github.com/RetroPortingToolKit/ndsrecomp/blob/e4a7f419/LICENSE)
- [ndsrecomp LICENSE-MIT](https://github.com/RetroPortingToolKit/ndsrecomp/blob/e4a7f419/LICENSE-MIT)
- [ndsrecomp LICENSE-GPL](https://github.com/RetroPortingToolKit/ndsrecomp/blob/e4a7f419/LICENSE-GPL)
- [ndsrecomp THIRD_PARTY_ATTRIBUTION](https://github.com/RetroPortingToolKit/ndsrecomp/blob/e4a7f419/THIRD_PARTY_ATTRIBUTION.md)
- [recomp-ui LICENSE (commit f3f99a96)](https://github.com/RetroPortingToolKit/recomp-ui/blob/f3f99a96/LICENSE)

Não assumir que commits mais antigos, uma licença do GitHub ou o estado atual de outra branch valham para o build fixado. O upstream documenta explicitamente que certas ferramentas e bancos gerados ficam fora da fronteira GPL; isso exige examinar a combinação concreta antes de redistribuí-la. As condições não comerciais não podem ser acrescentadas a uma obra coberta pela GPL.

## Inventário por fronteira de proveniência

| Caminho | Resultado da revisão |
| --- | --- |
| `.github/advanced/fuzz.py`, `.github/advanced/benchmark.py` | CI sintético original; MIT restrita aos dois arquivos. |
| `tools/`, `tests/`, `launcher/`, `android/`, scripts de build | Candidatos a licenciamento de contribuições próprias; verificar histórico, trechos copiados, cabeçalhos e dependências arquivo a arquivo. Não declarados MIT por esta revisão. |
| `patches/ndsrecomp-local.patch` | Patch de 1.266.078 bytes sobre upstream com licenças mistas. Exige classificação por arquivo/hunk e preservação dos avisos originais. O conector não retornou seu conteúdo integral, portanto não se presume licença. |
| `mods/` | Deltas, tradução, mods e metadados de terceiros. Créditos em CREDITS.md não equivalem a permissão de redistribuição. Conferir permissões por autor/versão. |
| `assets/` e screenshots | Arte, marcas, personagens e imagens do jogo: fora da MIT, sem nova autorização implícita. |
| `game.toml`, `recomplauncher.json`, docs | Configuração e documentação com metadados do jogo. Não altera direitos de terceiros ou do SDK. |
| `runtime/`, bancos C gerados, ROM e BIOS local | Artefatos de build dependentes da mídia e toolchain. Não incluídos nesta concessão MIT; não publicar dados de jogo sem autorização. |

## Gate de publicação real (manual)

Antes de publicar um novo binário:
1. Arquivar os hashes/commits exatos do build e listar os componentes efetivamente ligados ao executável.
2. Verificar licenças dos patches e bancos gerados, direitos de uso/distribuição de cada material e obrigações dos componentes PolyForm.
3. Para binário combinado GPL, preparar a forma de distribuição de código-fonte correspondente conforme GPL-3.0-or-later, incluindo alterações e scripts de build aplicáveis. Não afirmar que um patch isolado ou link upstream necessariamente cumpre todas as obrigações.
4. Incluir avisos/copyrights e textos de licença aplicáveis aos componentes redistribuídos. Verificar separadamente as permissões dos mods, tradução e arte.
5. Fazer auditoria do ZIP final e de releases históricas, sem remover ativos existentes automaticamente. Se direitos não puderem ser confirmados, não publicar o novo binário.
6. Registrar a revisão humana com evidência por versão. Atestação/SBOM não é uma autorização de licenciamento.

Esta é uma revisão técnica de proveniência, não uma opinião jurídica nem confirmação de que todos os binários já distribuídos estão conformes.
