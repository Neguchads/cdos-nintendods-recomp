# Contributing / Como contribuir

[English](#english) · [Português](#português)

## English

All help, ideas, pull requests, code reviews, testing, community support and improvements are welcome. You do not need to be a programmer to contribute.

### Future Castlevania research

We welcome research, ideas and contributions for the Dominus Collection / Nintendo DS trilogy and the three original GBA Castlevania games. See the [community expansion invitation](README.md#help-us-expand-the-castlevania-recompilation-ecosystem). Discuss feasibility and existing open-source efforts before proposing implementation; keep commercial ROMs and proprietary assets out of contributions.

### Before opening an issue

**Before opening an issue:** please search both open and closed issues and existing pull requests, check the [feature status and audit](docs/FEATURE_STATUS.md), [roadmap](ROADMAP.md), [release notes](https://github.com/Neguchads/cdos-nintendods-recomp/releases) and current game settings (F1). Confirm whether the feature or idea already exists, is planned, or has been reported. If a matching issue exists, add useful information there instead of creating a duplicate. If the existing feature is incomplete or broken, explain the missing behavior and include the version you tested. New ideas and genuine regressions are always welcome.

### Getting involved

- Use [Issues](https://github.com/Neguchads/cdos-nintendods-recomp/issues) for reproducible bugs and feature proposals; check existing issues first.
- Use [Discussions](https://github.com/Neguchads/cdos-nintendods-recomp/discussions) or [Discord](https://discord.gg/s7CWbpZJ) for questions, brainstorming and community support.
- For code or documentation changes, fork the repository, create a focused branch and open a [pull request](https://github.com/Neguchads/cdos-nintendods-recomp/pulls) describing the change, motivation, test results and known limitations. Reference the issue when applicable. Review existing PRs and offer constructive feedback.
- Include OS, release or commit, relevant settings, reproduction steps and expected versus actual behavior in bug reports. Redact private information.
- Follow the existing build and test instructions in the [English technical guide](README.en.md#clone-and-dependencies). Update the [feature registry](quality/features.json) and regenerate the dashboard when feature status changes, following [the quality policy](docs/FEATURE_ASSURANCE.md).
- Keep submissions clean-room: do not include commercial ROMs, BIOS, game data or third-party mods without permission. Follow the repository's [licensing review](docs/LICENSE_REVIEW.md) and [creator policy](docs/CREDITS.md). Respect other contributors.

Contributions of any size are appreciated; proposals are reviewed for correctness, scope, compatibility and maintainability.

## Português

Toda ajuda, ideias, pull requests, revisão de código, testes, suporte à comunidade e melhorias são bem-vindos. Você não precisa ser programador para contribuir.

### Pesquisa futura de Castlevania

São bem-vindas pesquisas, ideias e contribuições para a Dominus Collection / trilogia Nintendo DS e os três Castlevania originais de GBA. Consulte o [convite à comunidade](README.pt-BR.md#ajude-nos-a-expandir-o-ecossistema-de-recompilação-de-castlevania). Discuta a viabilidade e os projetos open source existentes antes de propor uma implementação; não inclua ROMs comerciais nem recursos proprietários nas contribuições.

### Antes de abrir uma issue

**Antes de abrir uma issue:** pesquise as issues abertas e fechadas e os pull requests existentes, consulte a [auditoria de funcionalidades](docs/FEATURE_STATUS.md), o [roadmap](ROADMAP.md), as [notas das versões](https://github.com/Neguchads/cdos-nintendods-recomp/releases) e as configurações atuais do jogo (F1). Verifique se a funcionalidade ou ideia já existe, está planejada ou foi relatada. Se houver uma issue correspondente, acrescente informações úteis nela em vez de criar uma duplicata. Se a funcionalidade existente estiver incompleta ou apresentar falhas, explique o que falta e informe a versão testada. Novas ideias e regressões reais são sempre bem-vindas.

### Como participar

- Use [Issues](https://github.com/Neguchads/cdos-nintendods-recomp/issues) para bugs reproduzíveis e propostas de funcionalidades; confira as issues existentes.
- Use [Discussions](https://github.com/Neguchads/cdos-nintendods-recomp/discussions) ou [Discord](https://discord.gg/s7CWbpZJ) para perguntas, ideias e suporte comunitário.
- Para alterar código ou documentação, faça um fork, crie uma branch específica e abra um [pull request](https://github.com/Neguchads/cdos-nintendods-recomp/pulls) descrevendo a alteração, motivação, resultados dos testes e limitações. Referencie a issue correspondente. Revisões construtivas de PRs também são bem-vindas.
- Em relatos de bugs, informe sistema operacional, versão ou commit, configurações relevantes, passos para reproduzir e comportamento esperado e observado. Remova informações privadas.
- Siga as instruções de compilação e testes do [guia em português](README.pt-BR.md#clone-e-dependências). Ao alterar o status de funcionalidades, atualize o [catálogo](quality/features.json) e regenere o dashboard conforme a [política de qualidade](docs/FEATURE_ASSURANCE.md).
- Preserve a política clean-room: não inclua ROMs comerciais, BIOS, dados do jogo ou mods de terceiros sem autorização. Respeite a [revisão de licenciamento](docs/LICENSE_REVIEW.md), a [política de criadores](docs/CREDITS.md) e os demais colaboradores.

Contribuições de qualquer tamanho são valorizadas; propostas serão avaliadas por correção, escopo, compatibilidade e facilidade de manutenção.

## Writing a release announcement / Como anunciar uma versão

Write English first, then Brazilian Portuguese. Include the GitHub release link and use these three sections.

Escreva primeiro em inglês e depois em português do Brasil. Inclua o link da versão no GitHub e use estas três seções.

- **What changed / O que mudou** — List user-facing changes and known limits. / Liste mudanças para quem joga e limites conhecidos.
- **What to test / O que testar** — Give a short checklist for the published build, including any required platform or game revision. / Passe uma lista curta de testes para a build publicada, com a plataforma ou edição do jogo exigida.
- **Where to report / Onde responder** — Link the game's Discord thread. Ask for the version, system, result, and reproduction steps. / Aponte para o tópico do jogo no Discord. Peça versão, sistema, resultado e passos para reproduzir.
