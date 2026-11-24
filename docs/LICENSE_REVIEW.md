# Licenciamento: revisão antes de uma licença principal

Este projeto reúne código original, configurações de integração, patches e
materiais relacionados a obras e ferramentas de terceiros. A ausência de uma
licença principal **não** significa que tudo esteja em domínio público.

## Pontos a verificar antes de aplicar MIT

- **Código original de Neguchads:** identificar arquivos específicos de autoria
  própria que possam ser oferecidos sob MIT, sem incluir código derivado
  incompatível.
- **RetroPortingToolKit/ndsrecomp:** conferir a licença de cada componente
  utilizado e preservar os avisos de atribuição. O projeto upstream documenta
  componentes MIT e requisitos adicionais para partes do runner.
- **Patches:** verificar a origem de cada trecho de código/patch e sua licença.
  Uma tradução ou patch binário não se torna MIT por estar neste repositório.
- **Imagens, logotipos, personagens e conteúdo de Castlevania:** pertencem aos
  respectivos titulares, não são cobertos por eventual licença MIT do código
  original do port.
- **Bibliotecas (SDL3, Dear ImGui etc.):** respeitar os avisos e condições
  específicos de seus autores.

## Próximas ações

1. Criar um inventário de arquivos de autoria própria versus componentes de
   terceiros (incluindo qualquer conteúdo gerado a partir de um ROM).
2. Mapear licenças e avisos exigidos para cada componente e distribuição.
3. Publicar um arquivo MIT restrito ao código original elegível, acompanhado
   de atribuições de terceiros; evitar uma licença global equivocada.

Referência upstream: https://github.com/RetroPortingToolKit/ndsrecomp

Esta nota é um checklist de proveniência, não uma autorização para
redistribuir conteúdo protegido nem uma conclusão jurídica.
