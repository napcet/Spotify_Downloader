# Spotify Music Downloader

A Python-based tool to download songs from Spotify playlists in various audio formats including **lossless FLAC from Deezer** (like Deezloader Telegram bot).

## Features

- 🎵 **Lossless FLAC downloads** from Deezer (premium quality)
- 📥 Download entire Spotify playlists, albums, or individual tracks
- 🎧 Multiple audio format support (FLAC, MP3, WAV, M4A, OPUS)
- 🎼 Automatic metadata tagging (artist, album, artwork, etc.)
- ⚡ Concurrent downloads for faster processing
- � Multi-source support (Deezer → YouTube fallback)
- �📋 Progress tracking and logging
- 🔍 Smart search matching
- 💾 Organized file structure by artist/album

## Prerequisites

- Python 3.8 or higher
- Spotify Developer Account (for API credentials)
- FFmpeg installed on your system

## Installation

1. Clone the repository:

```bash
cd Spotify_Downloader
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install FFmpeg:

   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

4. Set up Spotify API credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Copy your Client ID and Client Secret
   - Update `config/config.yaml` with your credentials

## Configuration

Edit `config/config.yaml`:

```yaml
spotify:
  client_id: "your_client_id"
  client_secret: "your_client_secret"

download:
  output_dir: "./downloads"
  audio_format: "mp3" # mp3, flac, wav, m4a
  audio_quality: "320" # for mp3: 128, 192, 256, 320
  max_concurrent: 3

preferences:
  embed_metadata: true
  embed_artwork: true
  organize_by_artist: true
```

## Usage

### Download a Playlist

```bash
python main.py --playlist <spotify_playlist_url>
```

### Download with Custom Format

```bash
python main.py --playlist <url> --format flac
```

### Download Single Track

```bash
python main.py --track <spotify_track_url> --format mp3 --quality 320
```

### Command Line Options

```
Options:
  --playlist URL        Spotify playlist URL
  --track URL          Spotify track URL
  --album URL          Spotify album URL
  --format FORMAT      Audio format (mp3, flac, wav, m4a) [default: mp3]
  --quality QUALITY    Audio quality for MP3 (128, 192, 256, 320) [default: 320]
  --output DIR         Output directory [default: ./downloads]
  --concurrent N       Number of concurrent downloads [default: 3]
  --no-metadata        Skip metadata embedding
  --no-artwork         Skip artwork embedding
  -h, --help          Show help message
```

## Examples

```bash
# Download playlist in FLAC format
python main.py --playlist https://open.spotify.com/playlist/xxxxx --format flac

# Download album in MP3 320kbps
python main.py --album https://open.spotify.com/album/xxxxx --format mp3 --quality 320

# Download to custom directory
python main.py --playlist https://open.spotify.com/playlist/xxxxx --output ~/Music/Spotify
```

## Project Structure

```
Spotify_Downloader/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   └── config.yaml        # Configuration file
├── src/
│   ├── __init__.py
│   ├── spotify_client.py  # Spotify API integration
│   ├── downloader.py      # Download logic
│   ├── youtube_search.py  # YouTube search
│   ├── converter.py       # Audio format conversion
│   ├── metadata.py        # Metadata tagging
│   └── utils.py           # Utility functions
└── downloads/             # Downloaded songs (created automatically)
```

## How It Works

1. **Fetch Metadata**: Retrieves track information from Spotify API
2. **Search YouTube**: Finds matching videos on YouTube
3. **Download Audio**: Downloads audio from YouTube
4. **Convert Format**: Converts to desired format using FFmpeg
5. **Add Metadata**: Embeds artist, title, album, artwork, etc.
6. **Organize Files**: Saves to organized directory structure

## Limitations

- Downloads are sourced from YouTube, so quality depends on available videos
- Requires active internet connection
- Respects rate limits of Spotify and YouTube APIs

## Legal Notice

This tool is for educational purposes only. Please respect copyright laws and only download music you have the right to access. Support artists by purchasing their music or using legitimate streaming services.

## Troubleshooting

- **FFmpeg not found**: Ensure FFmpeg is installed and in your system PATH
- **Spotify API errors**: Check your credentials in config.yaml
- **Download failures**: Some videos may not be available; the tool will skip them
- **Quality issues**: Try different search terms or download from different playlists

## License

MIT License - See LICENSE file for details
