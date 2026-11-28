# Shared native UI design system / Sistema visual nativo compartilhado

Status: **Proposed — not implemented or runtime-verified.** Tracking: [#65](https://github.com/Neguchads/cdos-nintendods-recomp/issues/65). Android [#52](https://github.com/Neguchads/cdos-nintendods-recomp/issues/52) and Linux [#63](https://github.com/Neguchads/cdos-nintendods-recomp/issues/63) remain independent deliverables.

## English

Use Windows as the first integration and regression-testing target for reusable native C++/Dear ImGui components. Reuse their semantics, bindings and navigation on Linux and Android. Do not introduce a second UI stack or assume Windows validation proves portability.

### Component contract

| Component | Behavior | Verification |
| --- | --- | --- |
| Card | Title, short description, optional icon, status and clear primary action | Legible at small sizes; meaningful text without color alone |
| Checkbox / toggle | Bound to an actual setting; explicit disabled reason | Change, persistence, reset and reload |
| Selection card | Mutually exclusive profile or layout choice | Exactly one selection; preserve existing config keys |
| Status card | Reports current value, capability or documented evidence | Unknown and unsupported are not represented as enabled |
| Collapsible group | Advanced settings with visible heading and focus | Keyboard/controller expansion and return focus |
| Proposal checklist | Documentation requirement and acceptance evidence | Checked only after the criterion is met; not a gameplay setting |

Use stable component IDs, localized strings, shared spacing and typography tokens, visible focus, and accessible text. Adapt columns to available space: one column on small displays, additional columns only when labels and controls fit. Avoid fixed pixel positioning or hardcoded 16:9 assumptions. Preserve original screen proportions.

### Integration boundaries

```text
Shared native widgets and theme
  -> Existing menu / settings and action bindings
  -> Platform adapters (input, display, storage, lifecycle)
     -> Windows | Linux | Android
```

This is a proposed architecture, not a claim about current source organization. Inspect the pinned upstream runtime and local patch before selecting actual file names or interfaces. Keep game state, renderer selection, configuration serialization and save formats independent of widget presentation.

### Windows-first implementation plan

- [ ] Audit existing F1 panels, localization, navigation and configuration bindings.
- [ ] Define common widgets and theme tokens; pilot Home and Screen & Layout.
- [ ] Test mouse, keyboard and controller focus, toggles, settings reload, and EN/PT-BR labels.
- [ ] Test 480×320, 640×480 and desktop sizes; avoid clipped controls or inaccessible scrolling.
- [ ] Extend Graphics, Audio, Controls, Mods & Campaigns, Performance & Dev; reuse components for future managers.
- [ ] Validate Direct3D 12 and Vulkan, save/config compatibility and UI overhead.
- [ ] Add shared single-screen map/status navigation while preserving original input actions; coordinate #62 and #64.
- [ ] Adapt platform-specific input, display and lifecycle behavior in the separate Linux and Android trackers. Test real devices before declaring support.

### Documentation and proposals

The existing [feature assurance policy](FEATURE_ASSURANCE.md) and `quality/features.json` remain the source of truth. Keep generated dashboard assets deterministic. Feature cards should show a stable requirement or issue link, scope, status, acceptance checklist and evidence. Do not manually duplicate progress percentages or treat checked settings as completed engineering work.

Example proposal:

**Single-screen navigation — planned**

- [ ] Gameplay retains the original aspect ratio.
- [ ] Configurable map and status access works using physical controls.
- [ ] Touch-dependent interactions have validated alternatives.
- [ ] Existing dual-screen layouts remain available.
- [ ] Evidence includes version, platform, renderer, configuration and result.

The checklist is an example, not completed work.

## Português (BR)

O Windows será a primeira plataforma de integração e validação dos componentes nativos em C++/Dear ImGui. Linux e Android reutilizarão os mesmos componentes, vínculos de estado e regras de navegação, com adaptadores específicos para entrada, telas, armazenamento e ciclo de vida.

**Componentes:** cards de recursos, caixas de seleção, seletores exclusivos, cards de estado, seções recolhíveis e checklists de propostas. Cada controle de jogo deve representar uma configuração real; caixas de conclusão de tarefas pertencem à documentação e exigem evidências.

**Regras:** preservar os nomes das configurações, saves, ações existentes, renderizadores e localização EN/PT-BR. Usar foco visível e layouts responsivos, com uma coluna nas telas pequenas. Não confundir aparência de card com implementação funcional.

**Etapas:** auditar F1; definir componentes comuns; integrar inicialmente Início e Tela & Layout no Windows; testar mouse, teclado, controle, 480×320, 640×480 e telas maiores; expandir às demais abas; validar Direct3D 12/Vulkan e persistência; integrar a navegação de tela única e, depois, adaptar os ports independentes.

O catálogo de funcionalidades existente continua sendo a fonte de verdade. Não publicar percentuais duplicados nem marcar funcionalidades como verificadas sem evidências específicas de plataforma.

**Limite atual:** este documento estabelece o padrão proposto. Nenhum componente do runtime foi integrado ou compilado nesta alteração.
