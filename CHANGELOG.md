# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.3] - 2025-12-04

### Adicionado

-

### Modificado

-

### Corrigido

- ***

## [1.0.1] - 2025-12-04

### Adicionado

- Sistema de versionamento profissional com arquivo VERSION
- Módulo `__version__.py` como fonte única de verdade para versão
- CHANGELOG.md seguindo padrões Keep a Changelog
- Versionamento dinâmico em setup.py e pyproject.toml
- Banner de versão dinâmico no módulo utils

### Modificado

- Centralização da versão para evitar inconsistências
- Organização da estrutura de versionamento do projeto

### Corrigido

- Sincronização de versões entre diferentes arquivos de configuração

---

## [1.0.0] - 2025-12-01

### Adicionado

- Sistema completo de download de músicas do Spotify
- Suporte para playlists, álbuns e faixas individuais
- Download de múltiplas fontes: Deemix, Internet Archive, Jamendo, YouTube
- Sistema de rastreamento de downloads para evitar duplicatas
- Suporte para múltiplos formatos de áudio (MP3, FLAC, M4A, OGG, OPUS)
- Embedação automática de metadados e artwork
- Sistema de organização de arquivos por artista/álbum
- Configuração via arquivo YAML
- Sistema de logging completo
- Barra de progresso e interface rica usando Rich
- Suporte para download concorrente configurável
- Detecção automática de FFmpeg
- Sistema de skip para arquivos já baixados
- Busca inteligente no YouTube com correspondência de duração

### Recursos

- Cliente Spotify para autenticação e busca de metadados
- Cliente Deemix para downloads de alta qualidade
- Cliente Internet Archive para conteúdo de domínio público
- Cliente Jamendo para músicas Creative Commons
- Busca no YouTube como fallback
- Sistema de progresso visual com Rich
- Rastreamento de downloads em JSON
- Validação de URLs do Spotify
- Formatação de duração e tamanho de arquivo

### Documentação

- README.md completo com instruções de instalação e uso
- Documentação de configuração
- Exemplos de uso

---

## Tipos de Mudanças

- **Adicionado** - para novas funcionalidades
- **Modificado** - para mudanças em funcionalidades existentes
- **Descontinuado** - para funcionalidades que serão removidas
- **Removido** - para funcionalidades removidas
- **Corrigido** - para correção de bugs
- **Segurança** - em caso de vulnerabilidades

---

## Formato de Versionamento

Este projeto usa [Versionamento Semântico](https://semver.org/lang/pt-BR/):

- **MAJOR** (X.0.0): Mudanças incompatíveis na API
- **MINOR** (0.X.0): Novas funcionalidades compatíveis com versões anteriores
- **PATCH** (0.0.X): Correções de bugs compatíveis com versões anteriores
