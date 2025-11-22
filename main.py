#!/usr/bin/env python3
"""
Spotify Music Downloader
Main entry point for the application.
Downloads Spotify playlists/albums/tracks in various formats including FLAC from Deezer.
"""

import sys
import click
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.spotify_client import SpotifyClient
from src.multi_source_downloader import MultiSourceDownloader
from src.metadata import MetadataEmbedder
from src.utils import (
    load_config, setup_logging, validate_spotify_url,
    check_ffmpeg, print_banner, ProgressTracker
)

logger = logging.getLogger('spotify_downloader')


@click.command()
@click.option('--playlist', '-p', help='Spotify playlist URL')
@click.option('--track', '-t', help='Spotify track URL')
@click.option('--album', '-a', help='Spotify album URL')
@click.option('--format', '-f', default=None, help='Audio format (mp3, flac, wav, m4a)')
@click.option('--quality', '-q', default=None, help='Audio quality for MP3 (128, 192, 256, 320)')
@click.option('--output', '-o', default=None, help='Output directory')
@click.option('--concurrent', '-c', default=None, type=int, help='Number of concurrent downloads')
@click.option('--no-metadata', is_flag=True, help='Skip metadata embedding')
@click.option('--no-artwork', is_flag=True, help='Skip artwork embedding')
@click.option('--config', default='config/config.yaml', help='Path to config file')
def main(playlist, track, album, format, quality, output, concurrent, no_metadata, no_artwork, config):
    """
    Spotify Music Downloader - Download playlists, albums, or tracks from Spotify.
    
    Supports high-quality FLAC downloads from Deezer (like Deezloader bot).
    
    Examples:
    
        \b
        # Download playlist in FLAC from Deezer
        python main.py --playlist <url> --format flac
        
        \b
        # Download album in MP3 320kbps
        python main.py --album <url> --format mp3 --quality 320
        
        \b
        # Download single track
        python main.py --track <url>
    """
    print_banner()
    
    # Check FFmpeg
    if not check_ffmpeg():
        click.echo("❌ FFmpeg not found! Please install FFmpeg to continue.")
        click.echo("   Ubuntu/Debian: sudo apt-get install ffmpeg")
        click.echo("   macOS: brew install ffmpeg")
        click.echo("   Arch: sudo pacman -S ffmpeg")
        click.echo("   Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)
    
    # Load configuration
    try:
        cfg = load_config(config)
    except Exception as e:
        click.echo(f"❌ Failed to load configuration: {e}")
        click.echo("   Make sure config/config.yaml exists and is valid")
        sys.exit(1)
    
    # Setup logging
    setup_logging(cfg)
    
    # Override config with command line arguments
    if format:
        cfg['download']['audio_format'] = format
    if quality:
        cfg['download']['audio_quality'] = quality
    if output:
        cfg['download']['output_dir'] = output
    if concurrent:
        cfg['download']['max_concurrent'] = concurrent
    if no_metadata:
        cfg['metadata']['embed_metadata'] = False
    if no_artwork:
        cfg['metadata']['embed_artwork'] = False
    
    # Validate input
    if not (playlist or track or album):
        click.echo("❌ Please provide a Spotify URL (--playlist, --track, or --album)")
        click.echo("   Use --help for more information")
        sys.exit(1)
    
    # Determine URL type
    url = playlist or track or album
    url_type = validate_spotify_url(url)
    
    if not url_type:
        click.echo("❌ Invalid Spotify URL")
        click.echo("   Expected format: https://open.spotify.com/playlist/xxxxx")
        sys.exit(1)
    
    try:
        # Initialize components
        click.echo("🔧 Initializing components...")
        
        # Initialize Spotify client
        try:
            spotify_client = SpotifyClient(
                cfg['spotify']['client_id'],
                cfg['spotify']['client_secret']
            )
        except Exception as e:
            click.echo(f"❌ Failed to initialize Spotify client: {e}")
            click.echo("   Please check your Spotify API credentials in config/config.yaml")
            click.echo("   Get credentials from: https://developer.spotify.com/dashboard")
            sys.exit(1)
        
        # Initialize multi-source downloader
        multi_downloader = MultiSourceDownloader(cfg)
        metadata_embedder = MetadataEmbedder(cfg)
        
        # Show available sources
        available_sources = multi_downloader.get_available_sources()
        if available_sources:
            sources_str = ', '.join([s.upper() for s in available_sources])
            click.echo(f"📡 Available sources: {sources_str}")
            
            # Show quality info
            if 'deezer' in available_sources and cfg['download']['audio_format'] == 'flac':
                click.echo("✨ FLAC quality enabled via Deezer (lossless)")
            elif cfg['download']['audio_format'] == 'flac':
                click.echo("⚠️  FLAC format selected but Deezer not configured")
                click.echo("   Will download from YouTube and convert to FLAC")
                click.echo("   For true lossless FLAC, configure Deezer in config.yaml")
        else:
            click.echo("⚠️  No download sources available")
            sys.exit(1)
        
        # Fetch tracks
        click.echo(f"🎵 Fetching {url_type} information...")
        
        if url_type == 'playlist':
            tracks = spotify_client.get_playlist_tracks(url)
        elif url_type == 'album':
            tracks = spotify_client.get_album_tracks(url)
        else:  # track
            tracks = [spotify_client.get_track(url)]
        
        if not tracks:
            click.echo("❌ No tracks found")
            sys.exit(1)
        
        click.echo(f"✅ Found {len(tracks)} track(s)")
        click.echo(f"📁 Output directory: {cfg['download']['output_dir']}")
        click.echo(f"🎼 Format: {cfg['download']['audio_format'].upper()}")
        
        if cfg['download']['audio_format'] == 'mp3':
            click.echo(f"🎚️  Quality: {cfg['download']['audio_quality']} kbps")
        
        click.echo()
        
        # Download tracks
        max_workers = cfg['download']['max_concurrent']
        progress_tracker = ProgressTracker(len(tracks))
        
        click.echo("🚀 Starting downloads...\n")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_track = {
                executor.submit(download_track, track, multi_downloader, metadata_embedder): track
                for track in tracks
            }
            
            # Process completed downloads with progress bar
            with tqdm(total=len(tracks), desc="Downloading", unit="track", ncols=100) as pbar:
                for future in as_completed(future_to_track):
                    track = future_to_track[future]
                    try:
                        success = future.result()
                        if success:
                            progress_tracker.update('completed')
                        else:
                            progress_tracker.update('failed')
                    except Exception as e:
                        logger.error(f"Error processing {track['name']}: {e}")
                        progress_tracker.update('failed')
                    
                    pbar.update(1)
                    pbar.set_postfix_str(f"✓ {progress_tracker.completed} ✗ {progress_tracker.failed}")
        
        # Print summary
        click.echo()
        click.echo("=" * 70)
        click.echo("📊 Download Summary:")
        click.echo(f"   ✅ Completed: {progress_tracker.completed}")
        click.echo(f"   ❌ Failed: {progress_tracker.failed}")
        click.echo(f"   ⊘ Skipped: {progress_tracker.skipped}")
        click.echo(f"   📁 Location: {cfg['download']['output_dir']}")
        click.echo("=" * 70)
        
        if progress_tracker.completed > 0:
            click.echo("\n🎉 Downloads completed successfully!")
            click.echo(f"   Check your files in: {cfg['download']['output_dir']}")
        elif progress_tracker.failed == len(tracks):
            click.echo("\n❌ All downloads failed. Please check the logs.")
            click.echo(f"   Log file: {cfg.get('logging', {}).get('file', 'downloads/download.log')}")
            sys.exit(1)
        else:
            click.echo("\n⚠️  Some downloads failed. Check the logs for details.")
    
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Download interrupted by user")
        click.echo("   Run the same command again to resume (existing files will be skipped)")
        sys.exit(0)
    except Exception as e:
        click.echo(f"\n❌ An error occurred: {e}")
        logger.exception("Fatal error")
        sys.exit(1)


def download_track(track, multi_downloader, metadata_embedder):
    """
    Download a single track from best available source.
    
    Args:
        track: Track dictionary from Spotify
        multi_downloader: MultiSourceDownloader instance
        metadata_embedder: MetadataEmbedder instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing: {track['artist']} - {track['name']}")
        
        # Download from best available source (Deezer → YouTube)
        audio_path = multi_downloader.download(track)
        if not audio_path:
            logger.error(f"Download failed for: {track['name']}")
            return False
        
        # Embed metadata (if not already embedded by source)
        if metadata_embedder.embed_metadata:
            metadata_embedder.embed(audio_path, track)
        
        logger.info(f"✓ Successfully downloaded: {track['artist']} - {track['name']}")
        return True
    
    except Exception as e:
        logger.error(f"Error downloading {track['name']}: {e}")
        return False


if __name__ == '__main__':
    main()
