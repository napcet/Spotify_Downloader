# Quick Start Guide

## 🎵 Download Spotify Playlists in FLAC Format

This tool downloads Spotify playlists, albums, and tracks in high-quality formats including **lossless FLAC** from Deezer (like Deezloader Telegram bot).

## 🚀 Quick Setup (5 minutes)

### 1. Run Setup Script

```bash
cd Spotify_Downloader
./setup.sh
```

Or manually:

```bash
pip install -r requirements.txt
```

### 2. Get Deezer ARL Token (for FLAC)

**Open Deezer in browser:**

1. Go to https://www.deezer.com and login
2. Press `F12` → `Application` → `Cookies` → `https://www.deezer.com`
3. Copy the `arl` cookie value

**Add to `config/config.yaml`:**

```yaml
deezer:
  arl_token: "your_arl_token_here"
  enabled: true

download:
  audio_format: "flac"
  source_priority: ["deezer", "youtube"]
```

### 3. Get Spotify API Credentials

1. Go to https://developer.spotify.com/dashboard
2. Create an app
3. Copy Client ID and Secret
4. Add to `config/config.yaml`

## 📥 Usage Examples

### Download Playlist in FLAC

```bash
python main.py --playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --format flac
```

### Download Album in MP3 320kbps

```bash
python main.py --album https://open.spotify.com/album/xxxxx --format mp3 --quality 320
```

### Download Single Track

```bash
python main.py --track https://open.spotify.com/track/xxxxx --format flac
```

### Custom Output Directory

```bash
python main.py --playlist <url> --output ~/Music/Spotify --format flac
```

## 🎼 Supported Formats

- **FLAC** - Lossless (from Deezer, like Deezloader) ⭐ Recommended
- **MP3** - 128/192/256/320 kbps
- **WAV** - Uncompressed
- **M4A** - AAC format
- **OPUS** - Modern codec

## 🔄 How It Works

```
Spotify → Deezer/YouTube → Download → Add Metadata → Organize Files
```

1. **Fetches** playlist/album info from Spotify
2. **Searches** Deezer for FLAC (or YouTube as fallback)
3. **Downloads** in your preferred format
4. **Embeds** metadata (title, artist, album, artwork)
5. **Organizes** by artist/album automatically

## 📊 Quality Comparison

| Source     | Format   | Bitrate       | Quality                 |
| ---------- | -------- | ------------- | ----------------------- |
| **Deezer** | **FLAC** | **1411 kbps** | **Lossless** ⭐⭐⭐⭐⭐ |
| YouTube    | MP3      | 320 kbps      | High ⭐⭐⭐             |

## ⚙️ Key Features

✅ **Lossless FLAC** from Deezer (like Deezloader bot)  
✅ **Batch download** entire playlists/albums  
✅ **Auto metadata** & high-res artwork  
✅ **Multi-source** (Deezer → YouTube fallback)  
✅ **Concurrent downloads** for speed  
✅ **Skip existing** files  
✅ **Organized folders** by artist/album

## 📁 Output Structure

```
downloads/
├── Artist Name/
│   └── Album Name/
│       ├── 01 - Artist - Track Name.flac
│       ├── 02 - Artist - Track Name.flac
│       └── folder.jpg
```

## 🔧 Configuration

Edit `config/config.yaml`:

```yaml
# Use Deezer for FLAC (like Deezloader)
deezer:
  arl_token: "your_token"
  enabled: true

# Download settings
download:
  output_dir: "./downloads"
  audio_format: "flac" # flac, mp3, wav, m4a
  audio_quality: "320" # for MP3: 128, 192, 256, 320
  max_concurrent: 3
  source_priority: ["deezer", "youtube"] # Try Deezer first

# Metadata
metadata:
  embed_metadata: true
  embed_artwork: true
  embed_lyrics: false

# Organization
organization:
  organize_by_artist: true
  filename_format: "{track_number:02d} - {artist} - {title}"
```

## 🆚 vs Deezloader Telegram Bot

| Feature            | This Tool | Deezloader Bot |
| ------------------ | --------- | -------------- |
| FLAC from Deezer   | ✅        | ✅             |
| Spotify playlists  | ✅        | ✅             |
| No Telegram needed | ✅        | ❌             |
| Open source        | ✅        | ❌             |
| Customizable       | ✅        | ❌             |
| Batch download     | ✅        | ✅             |
| CLI + automatable  | ✅        | ❌             |

## 🐛 Troubleshooting

**"Invalid ARL token"**

- Get a fresh token from your browser
- Make sure you're logged into Deezer

**"FFmpeg not found"**

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

**"Track not found on Deezer"**

- The tool automatically falls back to YouTube
- Some tracks may be region-restricted

**Slow downloads**

- Premium Deezer accounts are faster
- Reduce `max_concurrent` in config

## 📖 Detailed Documentation

- **FLAC_SETUP_GUIDE.md** - Detailed Deezer/FLAC setup
- **README.md** - Full documentation

## ⚖️ Legal Notice

- For **personal use** and **educational purposes** only
- Respect copyright laws in your jurisdiction
- **Support artists** by buying music or using official streaming
- Users are responsible for their own actions

## 🎯 Pro Tips

1. **Use Deezer for FLAC** - Set `source_priority: ["deezer", "youtube"]`
2. **Premium account** - Faster Deezer downloads
3. **Concurrent downloads** - Adjust `max_concurrent` based on your connection
4. **Skip existing** - Enable `skip_existing: true` to resume interrupted downloads
5. **Organize files** - Customize `folder_structure` and `filename_format`

## 🤝 Support

Check logs: `downloads/download.log`

---

**Enjoy your music in lossless quality! 🎵**
