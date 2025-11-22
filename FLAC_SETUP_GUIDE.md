# FLAC Download Setup Guide

## Overview

This Spotify downloader supports **high-quality FLAC downloads** using multiple methods:

1. **YouTube → FLAC Conversion** (Works out of the box)
2. **Deezer FLAC** (Requires additional setup - True lossless)

## Method 1: YouTube to FLAC (Easiest - Works Now!)

This method downloads from YouTube and converts to FLAC. While not "true lossless," YouTube's best audio quality is very good (opus ~160kbps or AAC ~256kbps).

### Setup

Already done! Just use:

```bash
python main.py --playlist <spotify_url> --format flac
```

✅ **Pros:** Works immediately, no extra setup  
❌ **Cons:** Not true lossless (converted from lossy source)

## Method 2: Deezer FLAC (True Lossless - Requires Setup)

Download actual lossless FLAC files from Deezer (like Deezloader bot).

### Prerequisites

1. **Deezer Account** (Free or Premium)
2. **ARL Token** from your Deezer account
3. **Deemix Library** installed

### Step 1: Install Deemix

Deemix is not on PyPI, install from source:

```bash
# Install deemix from GitLab
pip install git+https://gitlab.com/RemixDev/deemix-py.git
pip install deezer-py
```

**Note:** Deemix installation may fail due to dependencies. If it fails, you can still use Method 1 (YouTube to FLAC).

### Step 2: Get Your Deezer ARL Token

The ARL token is an authentication cookie that allows downloading from Deezer.

#### Using Browser (Recommended)

1. **Open Deezer** in your browser: https://www.deezer.com
2. **Log in** to your Deezer account
3. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I`
4. **Go to Application/Storage tab**:
   - Chrome/Edge: Click "Application" → "Cookies" → "https://www.deezer.com"
   - Firefox: Click "Storage" → "Cookies" → "https://www.deezer.com"
5. **Find the `arl` cookie**
6. **Copy the Value** (it's a long string of characters)

#### Important Notes:

- ⚠️ **Keep your ARL token private** - it's like a password
- ⚠️ The token expires if you log out or change your password
- ✅ Both free and premium Deezer accounts work
- ✅ Premium accounts get faster download speeds

### Step 3: Configure the Downloader

1. Open `config/config.yaml`

2. Add your ARL token and enable Deezer:

```yaml
# Deezer Configuration (for FLAC downloads)
deezer:
  arl_token: "your_arl_token_here" # Paste your ARL token
  enabled: true # Set to true to enable Deezer downloads

# Download Settings
download:
  output_dir: "./downloads"
  audio_format: "flac" # Set to flac for lossless quality
  audio_quality: "320"
  max_concurrent: 3
  skip_existing: true
  source_priority: ["deezer", "youtube"] # Try Deezer first, fallback to YouTube
```

3. Save the file

### Step 4: Download in FLAC Format

```bash
# Download playlist in FLAC from Deezer
python main.py --playlist https://open.spotify.com/playlist/xxxxx --format flac

# Download album in FLAC
python main.py --album https://open.spotify.com/album/xxxxx --format flac

# Download single track in FLAC
python main.py --track https://open.spotify.com/track/xxxxx --format flac
```

## How It Works

### With Deezer Configured:

```
Spotify → Search Deezer → Download FLAC → Embed Metadata → Done
          ↓ (if not found)
       Search YouTube → Download → Convert to FLAC → Embed Metadata
```

### Without Deezer:

```
Spotify → Search YouTube → Download → Convert to FLAC → Embed Metadata
```

## Quality Comparison

| Source         | Format   | Bitrate       | Quality Level           | True Lossless?     |
| -------------- | -------- | ------------- | ----------------------- | ------------------ |
| **Deezer**     | **FLAC** | **1411 kbps** | **Lossless ⭐⭐⭐⭐⭐** | **✅ Yes**         |
| YouTube → FLAC | FLAC     | Varies        | High ⭐⭐⭐⭐           | ❌ No (transcoded) |
| YouTube        | MP3      | 320 kbps      | High ⭐⭐⭐             | ❌ No              |

## Troubleshooting

### "deemix installation failed"

Deemix has dependency issues. If installation fails:

1. **Use YouTube to FLAC instead** (Method 1) - Still great quality!
2. Try installing in a fresh virtual environment
3. Check the deemix GitLab for issues: https://gitlab.com/RemixDev/deemix-py

### "Invalid ARL token" Error

- Your token may have expired
- Log out and log back into Deezer
- Get a fresh ARL token from your browser

### "Deezer/Deemix source not available"

The downloader will show available sources when you run it:

```
📡 Available sources: YOUTUBE
```

If you see only YouTube, deemix isn't installed or configured. The downloader will still work using YouTube!

### Track Not Found on Deezer

- The downloader will automatically fall back to YouTube
- Some tracks may only be available on YouTube
- Regional restrictions may apply

## Recommendation

**For most users:** Use **Method 1 (YouTube to FLAC)** - it's easier and produces excellent quality.

**For audiophiles:** Use **Method 2 (Deezer FLAC)** - true lossless, but requires setup.

The beauty of this downloader is it **automatically falls back** to YouTube if Deezer doesn't have the track!

## Alternative: spotdl

If deemix doesn't work, you can also try `spotdl`:

```bash
pip install spotdl
```

spotdl can download from YouTube with good quality and proper metadata.

## Legal Notice

⚠️ **Important**:

- This tool is for **educational purposes** and **personal use** only
- Downloading copyrighted content may violate Deezer's Terms of Service
- Users are responsible for complying with copyright laws in their jurisdiction
- **Support artists** by purchasing music or using legitimate streaming services
- Only download music you have the legal right to access

## Support

If you encounter issues:

1. Check the log file: `downloads/download.log`
2. Ensure FFmpeg is installed
3. Try Method 1 (YouTube to FLAC) if Method 2 fails
4. Verify your ARL token is valid (for Method 2)
5. Check your internet connection
