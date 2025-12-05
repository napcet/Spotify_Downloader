#!/usr/bin/env python3
"""
Script para atualizar a versão do projeto.
Uso: python bump_version.py [major|minor|patch] [--message "mensagem"]
"""

import sys
import argparse
from pathlib import Path
import re
from datetime import date


def read_version():
    """Lê a versão atual do arquivo VERSION."""
    version_file = Path("VERSION")
    if not version_file.exists():
        print("Erro: Arquivo VERSION não encontrado")
        sys.exit(1)
    return version_file.read_text().strip()


def parse_version(version_str):
    """Parse a versão em componentes major, minor, patch."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        print(f"Erro: Formato de versão inválido: {version_str}")
        sys.exit(1)
    return tuple(map(int, match.groups()))


def bump_version(current_version, bump_type):
    """Incrementa a versão de acordo com o tipo."""
    major, minor, patch = parse_version(current_version)
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        print(f"Erro: Tipo de bump inválido: {bump_type}")
        print("Use: major, minor ou patch")
        sys.exit(1)


def update_file(file_path, pattern, replacement):
    """Atualiza um arquivo substituindo um padrão."""
    path = Path(file_path)
    if not path.exists():
        print(f"Aviso: Arquivo não encontrado: {file_path}")
        return False
    
    content = path.read_text()
    new_content = re.sub(pattern, replacement, content)
    
    if content != new_content:
        path.write_text(new_content)
        print(f"✓ Atualizado: {file_path}")
        return True
    else:
        print(f"⊘ Sem mudanças: {file_path}")
        return False


def update_changelog(new_version):
    """Adiciona uma nova seção no CHANGELOG.md."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("Aviso: CHANGELOG.md não encontrado")
        return
    
    content = changelog_path.read_text()
    today = date.today().strftime("%Y-%m-%d")
    
    new_entry = f"""## [{new_version}] - {today}

### Adicionado
- 

### Modificado
- 

### Corrigido
- 

---

"""
    
    # Insere após o cabeçalho
    lines = content.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('## ['):
            insert_pos = i
            break
    
    if insert_pos > 0:
        lines.insert(insert_pos, new_entry.rstrip())
        changelog_path.write_text('\n'.join(lines))
        print(f"✓ CHANGELOG.md atualizado com seção para v{new_version}")
        print(f"  Por favor, edite CHANGELOG.md e preencha as mudanças")


def main():
    parser = argparse.ArgumentParser(
        description='Atualiza a versão do projeto',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python bump_version.py patch          # 1.0.1 → 1.0.2
  python bump_version.py minor          # 1.0.1 → 1.1.0
  python bump_version.py major          # 1.0.1 → 2.0.0
  
Após executar, lembre-se de:
  1. Editar CHANGELOG.md com as mudanças
  2. Fazer commit das alterações
  3. Criar tag: git tag -a vX.Y.Z -m "Release vX.Y.Z"
  4. Push: git push origin main --tags
        """
    )
    parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help='Tipo de incremento de versão'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostra o que seria feito sem fazer mudanças'
    )
    
    args = parser.parse_args()
    
    # Lê versão atual
    current_version = read_version()
    print(f"Versão atual: {current_version}")
    
    # Calcula nova versão
    new_version = bump_version(current_version, args.bump_type)
    print(f"Nova versão: {new_version}")
    
    if args.dry_run:
        print("\n[DRY RUN] Nenhuma mudança foi feita")
        return
    
    print("\nAtualizando arquivos...")
    
    # Atualiza VERSION
    Path("VERSION").write_text(new_version + '\n')
    print(f"✓ Atualizado: VERSION")
    
    # Atualiza pyproject.toml
    update_file(
        'pyproject.toml',
        r'version = "[^"]+"',
        f'version = "{new_version}"'
    )
    
    # Atualiza CHANGELOG.md
    update_changelog(new_version)
    
    print("\n✅ Versão atualizada com sucesso!")
    print(f"\nPróximos passos:")
    print(f"  1. Edite CHANGELOG.md e adicione as mudanças")
    print(f"  2. git add VERSION pyproject.toml CHANGELOG.md")
    print(f"  3. git commit -m 'chore: bump version to {new_version}'")
    print(f"  4. git tag -a v{new_version} -m 'Release v{new_version}'")
    print(f"  5. git push origin main --tags")


if __name__ == '__main__':
    main()
