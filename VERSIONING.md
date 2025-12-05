# Guia de Versionamento

Este documento descreve o sistema de versionamento do Spotify Downloader.

## Sistema de Versionamento

O projeto usa **Versionamento Semântico (SemVer)** no formato `MAJOR.MINOR.PATCH`:

- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Novas funcionalidades compatíveis com versões anteriores
- **PATCH**: Correções de bugs compatíveis com versões anteriores

### Exemplo

- `1.0.0` → `1.0.1`: Correção de bug
- `1.0.1` → `1.1.0`: Nova funcionalidade
- `1.1.0` → `2.0.0`: Mudança incompatível

## Estrutura de Arquivos

### 1. **VERSION** (Fonte única de verdade)

```
1.0.1
```

Este arquivo contém apenas o número da versão e é a fonte única de verdade para todo o projeto.

### 2. **src/**version**.py** (Módulo de versão)

```python
__version__ = "1.0.1"
__version_info__ = (1, 0, 1)
```

Lê a versão do arquivo `VERSION` e fornece metadados adicionais.

### 3. **setup.py** (Configuração dinâmica)

```python
version_file = Path(__file__).parent / "VERSION"
version = version_file.read_text().strip()
```

Lê a versão dinamicamente do arquivo `VERSION`.

### 4. **pyproject.toml** (Sincronizado manualmente)

```toml
version = "1.0.1"
```

Deve ser atualizado manualmente para corresponder ao `VERSION`.

## Como Atualizar a Versão

### Passo 1: Editar VERSION

```bash
echo "1.0.2" > VERSION
```

### Passo 2: Atualizar pyproject.toml

```toml
[project]
version = "1.0.2"
```

### Passo 3: Atualizar CHANGELOG.md

```markdown
## [1.0.2] - 2025-12-XX

### Corrigido

- Descrição das correções
```

### Passo 4: Commit e Tag

```bash
git add VERSION pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 1.0.2"
git tag -a v1.0.2 -m "Release v1.0.2"
git push origin main --tags
```

## Workflow de Release

1. **Desenvolvimento** → Branch `dev` ou `feature/*`
2. **Correções de Bug** → Incrementar PATCH
3. **Novas Features** → Incrementar MINOR
4. **Breaking Changes** → Incrementar MAJOR
5. **Atualizar CHANGELOG.md** com todas as mudanças
6. **Criar Git Tag** seguindo o padrão `vX.Y.Z`
7. **Publicar Release** no GitHub

## Acesso à Versão no Código

### Python

```python
from src.__version__ import __version__, __version_info__

print(f"Versão: {__version__}")
print(f"Versão Info: {__version_info__}")
```

### CLI

```python
from src.__version__ import VERSION_BANNER

print(VERSION_BANNER)
```

## Convenções de Commit

Use [Conventional Commits](https://www.conventionalcommits.org/) para mensagens de commit:

- `feat:` - Nova funcionalidade (MINOR)
- `fix:` - Correção de bug (PATCH)
- `docs:` - Mudanças na documentação
- `style:` - Formatação, ponto-e-vírgula, etc.
- `refactor:` - Refatoração de código
- `test:` - Adição de testes
- `chore:` - Manutenção (atualização de versão, deps, etc.)
- `BREAKING CHANGE:` - Mudança incompatível (MAJOR)

### Exemplos

```bash
git commit -m "feat: adicionar suporte para Apple Music"
git commit -m "fix: corrigir erro ao baixar playlists longas"
git commit -m "chore: bump version to 1.1.0"
git commit -m "feat!: remover suporte para Python 3.7"
```

## Checklist de Release

- [ ] Todos os testes passam
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado
- [ ] VERSION atualizado
- [ ] pyproject.toml sincronizado
- [ ] Commit com mensagem descritiva
- [ ] Tag Git criada
- [ ] Release publicado no GitHub
- [ ] PyPI atualizado (se aplicável)

## Automação Futura

Considere adicionar:

1. **GitHub Actions** para automatizar releases
2. **bump2version** ou **poetry version** para gerenciar versões
3. **Semantic Release** para versionamento automático
4. **Pre-commit hooks** para validar versões

## Referências

- [Semantic Versioning](https://semver.org/lang/pt-BR/)
- [Keep a Changelog](https://keepachangelog.com/pt-BR/)
- [Conventional Commits](https://www.conventionalcommits.org/)
