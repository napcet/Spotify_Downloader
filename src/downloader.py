"""
Audio Downloader Module
Handles downloading audio from YouTube and managing downloads.
"""

import yt_dlp
import os
from pathlib import Path
from typing import Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class Downloader:
    """Handles downloading audio files from YouTube."""
    
    def __init__(self, config: Dict):
        """
        Initialize downloader.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path(config.get('download', {}).get('output_dir', './downloads'))
        self.audio_format = config.get('download', {}).get('audio_format', 'mp3')
        self.audio_quality = config.get('download', {}).get('audio_quality', '320')
        self.skip_existing = config.get('download', {}).get('skip_existing', True)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self, youtube_url: str, track: Dict, progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Download audio from YouTube.
        
        Args:
            youtube_url: YouTube video URL
            track: Track metadata dictionary
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to downloaded file or None
        """
        output_path = self._get_output_path(track)
        
        # Check if file already exists
        if self.skip_existing and output_path.exists():
            logger.info(f"File already exists: {output_path}")
            return str(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_path.with_suffix('.%(ext)s')),
            'quiet': True,
            'no_warnings': True,
            'extract_audio': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self._get_codec(),
                'preferredquality': self.audio_quality,
            }],
        }
        
        # Add progress hook if callback provided
        if progress_callback:
            ydl_opts['progress_hooks'] = [progress_callback]
        
        try:
            logger.info(f"Downloading: {track['artist']} - {track['name']}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Find the downloaded file (yt-dlp may add extension)
            final_path = output_path.with_suffix(f'.{self._get_codec()}')
            
            if final_path.exists():
                logger.info(f"Successfully downloaded: {final_path}")
                return str(final_path)
            else:
                logger.error(f"Download completed but file not found: {final_path}")
                return None
        
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
    
    def _get_output_path(self, track: Dict) -> Path:
        """
        Generate output file path based on track metadata.
        
        Args:
            track: Track metadata dictionary
            
        Returns:
            Path object for output file
        """
        org_config = self.config.get('organization', {})
        
        # Get folder structure settings
        organize_by_artist = org_config.get('organize_by_artist', True)
        folder_structure = org_config.get('folder_structure', '{artist}/{album}/{track_number} - {title}')
        filename_format = org_config.get('filename_format', '{track_number:02d} - {artist} - {title}')
        
        # Clean strings for filesystem
        artist = self._sanitize_filename(track['artist'])
        album = self._sanitize_filename(track['album'])
        title = self._sanitize_filename(track['name'])
        track_number = track.get('track_number', 1)
        
        # Build path
        if organize_by_artist:
            base_path = self.output_dir / artist / album
        else:
            base_path = self.output_dir
        
        # Format filename
        filename = filename_format.format(
            artist=artist,
            title=title,
            album=album,
            track_number=track_number
        )
        
        return base_path / filename
    
    def _get_codec(self) -> str:
        """
        Get the appropriate codec for the audio format.
        
        Returns:
            Codec string
        """
        codec_map = {
            'mp3': 'mp3',
            'flac': 'flac',
            'wav': 'wav',
            'm4a': 'm4a',
            'opus': 'opus',
            'vorbis': 'vorbis'
        }
        return codec_map.get(self.audio_format.lower(), 'mp3')
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        return filename
