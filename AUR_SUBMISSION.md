# AUR Submission Guide

## ✅ Release Created!

**GitHub Release**: v1.0.0
**Release URL**: https://github.com/MokshitBindal/Spotify_Downloader/releases/tag/v1.0.0

## 📦 Files Ready for AUR

The following files are ready in this repository:
- ✅ `PKGBUILD` - Arch Linux package build script
- ✅ `.SRCINFO` - Package metadata for AUR
- ✅ `LICENSE` - MIT License

## 🚀 How to Submit to AUR

### Step 1: Create AUR Account
1. Go to https://aur.archlinux.org/register
2. Create an account (if you don't have one)
3. Add your SSH public key to your AUR account

### Step 2: Clone the AUR Repository
```bash
# Create a temporary directory
mkdir -p ~/aur-packages
cd ~/aur-packages

# Clone the AUR repository (will create empty repo)
git clone ssh://aur@aur.archlinux.org/spotify-downloader.git
cd spotify-downloader
```

### Step 3: Copy Files to AUR Repository
```bash
# Copy from your project
cp /home/Mokshit/Documents/Programming_files/My_Projects/Spotify_Downloader/PKGBUILD .
cp /home/Mokshit/Documents/Programming_files/My_Projects/Spotify_Downloader/.SRCINFO .

# Verify files
ls -la
```

### Step 4: Test the Package Locally
```bash
# Test build the package
makepkg -si

# If successful, the package will be installed on your system
# Test it:
spotify-downloader --help
```

### Step 5: Submit to AUR
```bash
# Add files to git
git add PKGBUILD .SRCINFO

# Commit
git commit -m "Initial upload: spotify-downloader v1.0.0"

# Push to AUR
git push origin master
```

### Step 6: Verify Submission
1. Visit: https://aur.archlinux.org/packages/spotify-downloader
2. You should see your package listed!

## 🔄 Updating the Package (Future Releases)

When you release a new version:

1. **Update version in your repo**:
   - Update `version` in `pyproject.toml`, `setup.py`
   - Update `pkgver` in `PKGBUILD`

2. **Create new GitHub release**:
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

3. **Update PKGBUILD**:
   ```bash
   # Download new tarball
   wget https://github.com/MokshitBindal/Spotify_Downloader/archive/v1.1.0.tar.gz
   
   # Calculate new SHA256
   sha256sum v1.1.0.tar.gz
   
   # Update sha256sums in PKGBUILD
   # Increment pkgrel if same version, or reset to 1 for new version
   ```

4. **Regenerate .SRCINFO**:
   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```

5. **Push to AUR**:
   ```bash
   cd ~/aur-packages/spotify-downloader
   cp /path/to/PKGBUILD .
   cp /path/to/.SRCINFO .
   git add PKGBUILD .SRCINFO
   git commit -m "Update to v1.1.0"
   git push origin master
   ```

## 📋 Package Information

**Package Name**: spotify-downloader
**Version**: 1.0.0
**Description**: Download Spotify playlists, albums, and tracks in FLAC/MP3 format from free sources
**URL**: https://github.com/MokshitBindal/Spotify_Downloader
**License**: MIT
**Dependencies**:
- python
- python-pip
- ffmpeg

**Optional Dependencies**:
- yt-dlp (YouTube download support)
- python-spotipy (Spotify API access)

## 🎯 Installation (After AUR Submission)

Users can install your package with:

```bash
# Using yay (AUR helper)
yay -S spotify-downloader

# Using paru (AUR helper)
paru -S spotify-downloader

# Manual installation
git clone https://aur.archlinux.org/spotify-downloader.git
cd spotify-downloader
makepkg -si
```

## 🐛 Troubleshooting

**SSH Key Issues**: Make sure your SSH key is added to AUR account
**Build Failures**: Test locally with `makepkg -si` before pushing
**Checksum Errors**: Regenerate SHA256 with `sha256sum <tarball>`
**.SRCINFO Outdated**: Always regenerate with `makepkg --printsrcinfo > .SRCINFO`

## 📚 AUR Guidelines

- Follow the [AUR submission guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- Respond to package comments and bug reports
- Keep the package updated with upstream releases
- Test the package before pushing updates

## ✨ Next Steps

1. Submit to AUR following steps above
2. Share the AUR link: `https://aur.archlinux.org/packages/spotify-downloader`
3. Add AUR installation instructions to your README
4. Monitor comments and update when needed

Good luck with your AUR submission! 🚀
