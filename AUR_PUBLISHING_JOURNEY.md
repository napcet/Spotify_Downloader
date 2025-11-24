# AUR Publishing Journey: A Complete Guide

**From Zero to Published Package on Arch User Repository**

This document chronicles the entire process of publishing `spotify-downloader` on the AUR, including all the issues encountered and how they were resolved. This serves as both a learning guide and reference for future package maintenance.

---

## 📚 Table of Contents

1. [Understanding the AUR](#understanding-the-aur)
2. [Pre-Publishing Preparation](#pre-publishing-preparation)
3. [Creating Packaging Files](#creating-packaging-files)
4. [Issues and Solutions](#issues-and-solutions)
5. [Creating GitHub Releases](#creating-github-releases)
6. [AUR Account Setup](#aur-account-setup)
7. [Testing the Package](#testing-the-package)
8. [Publishing to AUR](#publishing-to-aur)
9. [Maintenance and Updates](#maintenance-and-updates)
10. [Lessons Learned](#lessons-learned)

---

## Understanding the AUR

### What is the AUR?

The **Arch User Repository (AUR)** is a community-driven repository for Arch Linux users. It contains package descriptions (PKGBUILDs) that allow you to compile a package from source and install it with `makepkg`.

### Key Concepts:

- **PKGBUILD**: A shell script containing build instructions and metadata
- **.SRCINFO**: Machine-readable metadata generated from PKGBUILD
- **makepkg**: Tool that builds packages from PKGBUILD
- **Source Tarball**: Your application's source code, typically from GitHub releases

### How AUR Works:

1. User clones AUR repository via SSH
2. `makepkg` downloads source tarball from GitHub
3. Package is built according to PKGBUILD instructions
4. Resulting `.pkg.tar.zst` file can be installed with `pacman`

---

## Pre-Publishing Preparation

### 1. Repository Cleanup

**Goal**: Keep only essential files tracked in Git

**What We Did:**

```bash
# Updated .gitignore to exclude:
- Extra documentation (API_PROVIDERS.md, FREE_*.md, etc.)
- Helper scripts (download_missed.py, quick-setup.sh, etc.)
- Build artifacts (__pycache__/, dist/, build/)
- Runtime files (.user_config.json, downloads/)
```

**Why**: AUR packages build from source tarballs. Extra files increase download size and aren't needed for building.

**Result**: Lean repository with only:

- `main.py` (entry point)
- `src/` (source code)
- `requirements.txt` (dependencies)
- `README.md` (documentation)
- Packaging files (PKGBUILD, setup.py, etc.)

### 2. Removing Redundant Files

**Issue**: Found duplicate/unused files in `src/`

**Investigation:**

```bash
# Checked imports across all files
grep -r "converter" src/
grep -r "deezer_client" src/
```

**Found**:

- `converter.py` - Never imported or used
- `deezer_client.py` - Duplicate (we use `deemix_client.py`)

**Solution**:

```bash
git rm src/converter.py src/deezer_client.py
# Updated src/__init__.py to remove references
```

**Lesson**: Always verify what's actually used before packaging.

---

## Creating Packaging Files

### 1. Python Packaging Files

#### **pyproject.toml** (Modern Python standard)

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "spotify-downloader"
version = "1.0.2"
description = "Download Spotify playlists..."
dependencies = [
    "spotipy>=2.24.0",
    "yt-dlp>=2024.10.7",
    # ... other deps
]

[project.scripts]
spotify-downloader = "main:main"
spotdl = "main:main"  # Short alias
```

**Key Points**:

- `[project.scripts]` creates executable commands
- Version must match PKGBUILD
- Dependencies list all runtime requirements

#### **setup.py** (Backward compatibility)

```python
setup(
    name="spotify-downloader",
    version="1.0.2",
    py_modules=["main"],  # Include main.py as module
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "spotify-downloader=main:main",
            "spotdl=main:main",
        ],
    },
)
```

**Critical**: `py_modules=["main"]` tells setuptools to include `main.py`

#### **MANIFEST.in** (Include extra files)

```
include README.md
include LICENSE
include requirements.txt
recursive-include src *.py
global-exclude __pycache__
```

### 2. PKGBUILD (Arch Package Script)

```bash
# Maintainer: Mokshit Bindal <mokshit112005@gmail.com>

pkgname=spotify-downloader
pkgver=1.0.2
pkgrel=1
pkgdesc="Download Spotify playlists, albums, and tracks..."
arch=('any')  # Pure Python, not architecture-specific
url="https://github.com/MokshitBindal/Spotify_Downloader"
license=('MIT')
depends=('python' 'python-pip' 'ffmpeg')
makedepends=('python-setuptools' 'python-build' 'python-installer' 'python-wheel')
source=("${pkgname}-${pkgver}.tar.gz::https://github.com/MokshitBindal/Spotify_Downloader/archive/v${pkgver}.tar.gz")
sha256sums=('bbbbf9633a607543e45494af2469495895a262925bda2f31150a2f3028d6c8df')

build() {
    cd "${srcdir}/Spotify_Downloader-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${srcdir}/Spotify_Downloader-${pkgver}"
    python -m installer --destdir="$pkgdir" dist/*.whl

    install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
```

**Important Details**:

- `arch=('any')` for pure Python packages
- `srcdir` path matches extracted folder name (repo name, not package name)
- SHA256 checksum must match the tarball exactly

### 3. .SRCINFO (Generated metadata)

```bash
makepkg --printsrcinfo > .SRCINFO
```

Never edit manually - always regenerate from PKGBUILD!

---

## Issues and Solutions

### Issue #1: Package Not Executable

**Problem**: Users would have to run `python main.py` instead of just `spotify-downloader`

**Root Cause**: Missing `py_modules=["main"]` in packaging configuration

**Investigation**:

```bash
# Checked wheel contents
unzip -p dist/*.whl spotify_downloader-1.0.0.dist-info/entry_points.txt
# Result: Entry points existed but main.py wasn't packaged
```

**Solution**:

1. Added `py_modules=["main"]` to `setup.py` and `pyproject.toml`
2. This tells setuptools to include `main.py` as a Python module
3. Entry points can now properly reference `main:main`

**Testing**:

```bash
python -m build --wheel
unzip -l dist/*.whl  # Verified main.py is included
```

**Version**: Fixed in v1.0.1

---

### Issue #2: Wrong Architecture Type

**Problem**: PKGBUILD had `arch=('x86_64')` for pure Python code

**Why This Matters**: Pure Python packages work on any architecture (x86_64, aarch64, etc.)

**Solution**: Changed to `arch=('any')`

**Lesson**: Use `x86_64` only for compiled binaries, use `any` for interpreted languages.

---

### Issue #3: GitHub Repository URL Mismatch

**Problem**: PKGBUILD referenced lowercase `spotify-downloader` but repo was `Spotify_Downloader`

**Symptoms**:

- Source URL 404 errors
- Tarball download failures
- SHA256 mismatches

**Solution**:

1. Updated all URLs to use actual repo name: `Spotify_Downloader`
2. Updated `srcdir` path to match extracted folder name
3. Verified tarball downloads and extracts correctly

```bash
# Test download
wget https://github.com/MokshitBindal/Spotify_Downloader/archive/v1.0.1.tar.gz
tar -tzf v1.0.1.tar.gz | head -5  # Check extracted folder name
```

**Files Updated**:

- PKGBUILD (source URL and srcdir paths)
- setup.py (project URLs)
- pyproject.toml (project URLs)

---

### Issue #4: SHA256 Checksum Calculation

**Problem**: PKGBUILD had `sha256sums=('SKIP')` - insecure and AUR won't accept it

**Process**:

```bash
# Download the exact tarball that makepkg will use
wget https://github.com/MokshitBindal/Spotify_Downloader/archive/v1.0.2.tar.gz

# Calculate checksum
sha256sum v1.0.2.tar.gz
# Result: bbbbf9633a607543e45494af2469495895a262925bda2f31150a2f3028d6c8df

# Update PKGBUILD
sha256sums=('bbbbf9633a607543e45494af2469495895a262925bda2f31150a2f3028d6c8df')
```

**Important**: Checksum must be recalculated for EVERY new release!

---

### Issue #5: Missing Build Dependencies

**Problem**: Build failed with `ERROR Missing dependencies: setuptools_scm>=6.2`

**Root Cause**: `pyproject.toml` required `setuptools_scm` in build requirements

**Why It Failed**:

- We hardcode version numbers, don't need dynamic versioning
- `setuptools_scm` is for git-based version detection
- Not available in clean build environments

**Solution**:

```toml
# Before
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm>=6.2"]

# After
[build-system]
requires = ["setuptools>=45", "wheel"]
```

**Testing**:

```bash
cd /tmp
git clone https://github.com/MokshitBindal/Spotify_Downloader.git test-build
cd test-build
python -m build --wheel  # Must succeed without setuptools_scm
```

**Version**: Fixed in v1.0.2

---

### Issue #6: Virtual Environment Interference

**Problem**: Build used venv Python instead of system Python

**Symptoms**:

```
/home/Mokshit/.../venv/bin/python: No module named build
ERROR: A failure occurred in build()
```

**Cause**: Active virtual environment when running makepkg

**Solution**:

```bash
deactivate  # Exit venv
unset VIRTUAL_ENV  # Clear environment variable
makepkg --cleanbuild  # Build with system Python
```

**Best Practice**: Always build AUR packages outside virtual environments

---

### Issue #7: Git Branch Naming (AUR Requirement)

**Problem**: Tried to push to `main` branch, AUR rejected it

**Error Message**:

```
remote: error: pushing to a branch other than master is restricted
! [remote rejected] main -> main (hook declined)
```

**Cause**: AUR requires the `master` branch specifically (legacy naming)

**Solution**:

```bash
git branch -M main master  # Rename branch
git push origin master     # Push to master
```

**Why**: AUR infrastructure predates GitHub's main/master transition

---

## Creating GitHub Releases

### Why Releases Matter

AUR packages download from GitHub release tarballs. Without releases:

- Users download from random commits
- No stable reference points
- Difficult to track versions

### Release Process

#### 1. Update Version Numbers

**Files to update** (must all match!):

- `pyproject.toml`: `version = "1.0.2"`
- `setup.py`: `version="1.0.2"`
- `PKGBUILD`: `pkgver=1.0.2`

#### 2. Commit Changes

```bash
git add pyproject.toml setup.py PKGBUILD
git commit -m "Bump version to 1.0.2"
git push origin main
```

#### 3. Create Annotated Tag

```bash
git tag -a v1.0.2 -m "v1.0.2: Fix build dependencies

Changes:
- Removed setuptools_scm requirement
- Fixed executable entry points
- Updated documentation"
```

**Why annotated tags?** They include:

- Author information
- Date/timestamp
- Detailed message
- Can be signed with GPG

#### 4. Push Tag

```bash
git push origin v1.0.2
```

This creates a release on GitHub automatically!

#### 5. Calculate Tarball SHA256

```bash
# Download the release tarball
wget https://github.com/MokshitBindal/Spotify_Downloader/archive/v1.0.2.tar.gz

# Calculate checksum
sha256sum v1.0.2.tar.gz

# Update PKGBUILD with this checksum
```

### Version Progression

- **v1.0.0**: Initial release with packaging files
- **v1.0.1**: Fixed executable entry points
- **v1.0.2**: Removed setuptools_scm dependency (final published version)

---

## AUR Account Setup

### 1. Create AUR Account

**URL**: https://aur.archlinux.org/register

**Required Information**:

- Username: `Archer` (your system username)
- Email: `mokshit112005@gmail.com`
- Backup Email: `mokshit020121@gmail.com`
- SSH Public Key: Essential for package submission

### 2. Generate SSH Key (if needed)

```bash
# Check for existing key
ls -la ~/.ssh/id_*.pub

# Generate new key (if needed)
ssh-keygen -t ed25519 -C "mokshit112005@gmail.com"

# Display public key
cat ~/.ssh/id_ed25519.pub
```

**Your Key**:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOUE7w7gF3rG8bxpRH7iLcSml98+KqaolO4U553o9lNg Mokshit@Archer
```

### 3. Anti-Bot Protection

AUR requires solving a command to prevent automated signups:

```bash
LC_ALL=C pacman -V|sed -r 's#[0-9]+#843#g'|md5sum|cut -c1-6
# Result: 54ce77
```

**What it does**:

1. Gets pacman version
2. Replaces all numbers with "843"
3. Calculates MD5 hash
4. Takes first 6 characters

### 4. Account Settings

**Recommended**:

- ☐ Hide Email: Unchecked (so users can contact you)
- ☑ Notify of new comments: Checked
- ☑ Notify of package updates: Checked
- ☑ Notify of ownership updates: Checked

---

## Testing the Package

### Local Build Test

**Always test locally before pushing to AUR!**

```bash
# Create test directory
mkdir -p ~/aur-test
cd ~/aur-test

# Copy package files
cp /path/to/PKGBUILD .
cp /path/to/.SRCINFO .

# Test build
makepkg --cleanbuild --syncdeps

# Inspect built package
tar -tzf spotify-downloader-1.0.2-1-any.pkg.tar.zst | less
```

### Test Installation

```bash
# Install locally built package
sudo pacman -U spotify-downloader-1.0.2-1-any.pkg.tar.zst

# Test commands
spotify-downloader --help
spotdl --version

# Test functionality
spotify-downloader --song "test song"
```

### Verify Files

```bash
# Check installed files
pacman -Ql spotify-downloader

# Expected output:
# /usr/bin/spotify-downloader
# /usr/bin/spotdl
# /usr/lib/python3.13/site-packages/...
# /usr/share/doc/spotify-downloader/README.md
# /usr/share/licenses/spotify-downloader/LICENSE
```

### Common Build Issues

**Issue**: Module not found during build

- **Fix**: Add to `depends` in PKGBUILD

**Issue**: File not included in package

- **Fix**: Update MANIFEST.in or package_data

**Issue**: Command not working after install

- **Fix**: Check entry_points in setup.py

---

## Publishing to AUR

### 1. Clone AUR Repository

```bash
# Create directory for AUR packages
mkdir -p ~/Documents/Programming_files/My_Projects

# Clone your package's AUR repo (creates empty repo)
cd ~/Documents/Programming_files/My_Projects
git clone ssh://aur@aur.archlinux.org/spotify-downloader.git spotify-downloader-aur
```

**First-time SSH Connection**:

You'll see:

```
The authenticity of host 'aur.archlinux.org' can't be established.
ED25519 key fingerprint is SHA256:RFzBCUItH9LZS0cKB5UE6ceAYhBD5C8GeOBip8Z11+4
Are you sure you want to continue connecting (yes/no)?
```

**Verify fingerprint matches official**:

- Ed25519: `SHA256:RFzBCUItH9LZS0cKB5UE6ceAYhBD5C8GeOBip8Z11+4` ✓
- ECDSA: `SHA256:uTa/0PndEgPZTf76e1DFqXKJEXKsn7m9ivhLQtzGOCI`
- RSA: `SHA256:5s5cIyReIfNNVGRFdDbe3hdYiI5OelHGpw2rOUud3Q8`

Type `yes` only if fingerprint matches!

### 2. Copy Package Files

```bash
cd spotify-downloader-aur

# Copy from your development directory
cp ../Spotify_Downloader/PKGBUILD .
cp ../Spotify_Downloader/.SRCINFO .

# Verify
ls -la
# Should show: PKGBUILD, .SRCINFO, .git/
```

### 3. Test Build in AUR Directory

```bash
# Clean build
makepkg --cleanbuild

# If successful, you'll see:
# ==> Finished making: spotify-downloader 1.0.2-1
```

### 4. Commit and Push

```bash
# Add files
git add PKGBUILD .SRCINFO

# Commit with descriptive message
git commit -m "Initial upload: spotify-downloader v1.0.2

Multi-source Spotify music downloader with beautiful terminal UI

Features:
- Download from Internet Archive (FLAC), Jamendo (CC), and YouTube
- Beautiful fixed-position progress display
- Smart retry system for failed downloads
- Interactive preferences wizard
- Multiple format support
- No premium accounts required"

# Push to master (not main!)
git push origin master
```

**Important**: AUR requires `master` branch, not `main`!

If you accidentally created main:

```bash
git branch -M main master
git push origin master
```

### 5. Verify Publication

Visit: https://aur.archlinux.org/packages/spotify-downloader

You should see:

- Package name and version
- Description
- Dependencies
- Your name as maintainer
- Package files (PKGBUILD, .SRCINFO)

---

## Maintenance and Updates

### Updating to New Version

#### 1. Prepare New Release

```bash
cd ~/Documents/Programming_files/My_Projects/Spotify_Downloader

# Update version in all files
vim pyproject.toml  # version = "1.0.3"
vim setup.py        # version="1.0.3"
vim PKGBUILD        # pkgver=1.0.3

# Commit and tag
git add -A
git commit -m "Bump version to 1.0.3"
git tag -a v1.0.3 -m "v1.0.3: Description of changes"
git push origin main
git push origin v1.0.3
```

#### 2. Update PKGBUILD

```bash
# Download new tarball
wget https://github.com/MokshitBindal/Spotify_Downloader/archive/v1.0.3.tar.gz

# Calculate new checksum
sha256sum v1.0.3.tar.gz

# Update PKGBUILD
# - pkgver=1.0.3
# - pkgrel=1 (reset to 1 for new version)
# - sha256sums=('new_checksum_here')

# Regenerate .SRCINFO
makepkg --printsrcinfo > .SRCINFO
```

#### 3. Test and Push Update

```bash
# Test build
makepkg --cleanbuild

# Copy to AUR directory
cd ~/Documents/Programming_files/My_Projects/spotify-downloader-aur
cp ../Spotify_Downloader/PKGBUILD .
cp ../Spotify_Downloader/.SRCINFO .

# Commit and push
git add PKGBUILD .SRCINFO
git commit -m "Update to v1.0.3

Changes:
- Feature 1
- Feature 2
- Bug fixes"
git push origin master
```

### Handling Bug Reports

Users can comment on your AUR page. Monitor notifications!

**Common user issues**:

1. Missing dependencies → Add to `depends` or `makedepends`
2. Build failures → Test in clean environment
3. Runtime errors → Fix in your code, release new version

### Marking Package Out-of-Date

If you don't update for a while, users can flag as out-of-date. Respond promptly!

---

## Lessons Learned

### 1. **Test in Clean Environments**

**Mistake**: Tested only in development environment with venv
**Problem**: Build failed for users due to missing system packages
**Solution**: Always test with `makepkg --cleanbuild` outside venv

### 2. **Version Numbers Must Match Everywhere**

**Critical Files**:

- pyproject.toml
- setup.py
- PKGBUILD
- Git tag

**One mismatch** = confused users and broken builds

### 3. **SHA256 is Non-Negotiable**

**Never use** `sha256sums=('SKIP')`

- Security risk
- AUR won't accept it
- Users won't trust it

### 4. **Read the Error Messages**

Every error taught something:

- "pushing to branch other than master" → AUR uses master
- "Missing dependencies: setuptools_scm" → Remove unused deps
- "No module named build" → Wrong Python environment

### 5. **Documentation Matters**

**Created multiple docs**:

- README.md (users)
- AUR_SUBMISSION.md (maintainers)
- AUR_PUBLISHING_JOURNEY.md (learning)

Different audiences need different information!

### 6. **Start Simple, Iterate**

**Version progression**:

- v1.0.0: Basic functionality
- v1.0.1: Fixed entry points
- v1.0.2: Fixed build deps

**Don't aim for perfection first time** - iterate based on feedback

### 7. **Community is Key**

**Before publishing**:

- Searched existing packages (spotdl, ytmdl, etc.)
- Read AUR submission guidelines
- Checked best practices

**After publishing**:

- Monitor comments
- Respond to issues
- Keep package updated

---

## Quick Reference Commands

### Build and Test

```bash
# Generate .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# Clean build
makepkg --cleanbuild

# Install locally
makepkg -si

# Check package contents
tar -tzf *.pkg.tar.zst | less
```

### Git Operations

```bash
# Create release
git tag -a v1.0.2 -m "Release message"
git push origin v1.0.2

# Calculate checksum
sha256sum tarball.tar.gz

# AUR push
git push origin master  # Not main!
```

### Debugging

```bash
# Check installed files
pacman -Ql spotify-downloader

# Check dependencies
pactree spotify-downloader

# Remove package
sudo pacman -R spotify-downloader
```

---

## Resources

### Official Documentation

- [AUR Submission Guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- [PKGBUILD](https://wiki.archlinux.org/title/PKGBUILD)
- [Creating Packages](https://wiki.archlinux.org/title/Creating_packages)
- [Python Package Guidelines](https://wiki.archlinux.org/title/Python_package_guidelines)

### Our Package

- **AUR Page**: https://aur.archlinux.org/packages/spotify-downloader
- **GitHub**: https://github.com/MokshitBindal/Spotify_Downloader
- **Maintainer**: Archer (Mokshit Bindal)

### Community

- **AUR Mailing List**: https://lists.archlinux.org/listinfo/aur-general
- **Arch Forums**: https://bbs.archlinux.org/
- **IRC**: #archlinux-aur on Libera.Chat

---

## Conclusion

Publishing to AUR is a journey of:

1. **Preparation**: Clean code, proper structure
2. **Packaging**: PKGBUILD, .SRCINFO, metadata
3. **Testing**: Build, install, verify
4. **Publishing**: SSH, Git, community interaction
5. **Maintenance**: Updates, bug fixes, user support

**Key takeaway**: Every error is a learning opportunity. Document your journey so others (and future you) can benefit!

**Status**: `spotify-downloader` is now LIVE on AUR! 🎉

**Installation**:

```bash
yay -S spotify-downloader
# or
paru -S spotify-downloader
```

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2025  
**Package Version**: 1.0.2  
**Status**: Published ✅
