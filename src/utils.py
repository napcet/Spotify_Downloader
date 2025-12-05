"""
Utility Functions
Helper functions for configuration, logging, and file operations.
"""

import yaml
import logging
import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
import sys
from .__version__ import __version__, VERSION_BANNER


def load_config(config_path: str = 'config/config.yaml') -> Dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"Configuration file not found: {config_path}")
            print("Creating default configuration...")
            create_default_config(config_path)
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables if available
        if os.getenv('SPOTIFY_CLIENT_ID'):
            config['spotify']['client_id'] = os.getenv('SPOTIFY_CLIENT_ID')
        if os.getenv('SPOTIFY_CLIENT_SECRET'):
            config['spotify']['client_secret'] = os.getenv('SPOTIFY_CLIENT_SECRET')
        if os.getenv('OUTPUT_DIR'):
            config['download']['output_dir'] = os.getenv('OUTPUT_DIR')
        
        return config
    
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def create_default_config(config_path: str):
    """
    Create a default configuration file.
    
    Args:
        config_path: Path where config file should be created
    """
    default_config = {
        'spotify': {
            'client_id': 'YOUR_SPOTIFY_CLIENT_ID',
            'client_secret': 'YOUR_SPOTIFY_CLIENT_SECRET'
        },
        'download': {
            'output_dir': './downloads',
            'audio_format': 'mp3',
            'audio_quality': '320',
            'max_concurrent': 3,
            'skip_existing': True
        },
        'audio': {
            'sample_rate': 48000,
            'bitrate': 320,
            'channels': 2
        },
        'metadata': {
            'embed_metadata': True,
            'embed_artwork': True,
            'embed_lyrics': False
        },
        'organization': {
            'organize_by_artist': True,
            'folder_structure': '{artist}/{album}/{track_number} - {title}',
            'filename_format': '{track_number:02d} - {artist} - {title}'
        },
        'youtube': {
            'search_query_format': '{artist} {title} audio',
            'max_results': 5,
            'prefer_official': True,
            'min_duration_match': 0.9,
            'max_duration_match': 1.1
        },
        'logging': {
            'level': 'INFO',
            'file': './downloads/download.log',
            'console': True
        }
    }
    
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Default configuration created at: {config_path}")
    print("Please update it with your Spotify API credentials.")


def setup_logging(config: Dict) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger
    """
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', './downloads/download.log')
    console_logging = log_config.get('console', True)
    
    # Create logger
    logger = logging.getLogger('spotify_downloader')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def format_duration(milliseconds: int) -> str:
    """
    Format duration from milliseconds to MM:SS format.
    
    Args:
        milliseconds: Duration in milliseconds
        
    Returns:
        Formatted duration string
    """
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def format_size(bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def validate_spotify_url(url: str) -> Optional[str]:
    """
    Validate and extract Spotify URL type.
    
    Args:
        url: Spotify URL
        
    Returns:
        URL type ('playlist', 'track', 'album') or None if invalid
    """
    if 'spotify.com/playlist/' in url or 'spotify:playlist:' in url:
        return 'playlist'
    elif 'spotify.com/track/' in url or 'spotify:track:' in url:
        return 'track'
    elif 'spotify.com/album/' in url or 'spotify:album:' in url:
        return 'album'
    return None


def check_ffmpeg() -> bool:
    """
    Check if FFmpeg is installed and accessible.
    
    Returns:
        True if FFmpeg is available, False otherwise
    """
    import subprocess
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def print_banner():
    """Print application banner."""
    print(VERSION_BANNER)


class ProgressTracker:
    """Track download progress."""
    
    def __init__(self, total: int):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items
        """
        self.total = total
        self.completed = 0
        self.failed = 0
        self.skipped = 0
    
    def update(self, status: str = 'completed'):
        """
        Update progress.
        
        Args:
            status: Status ('completed', 'failed', 'skipped')
        """
        if status == 'completed':
            self.completed += 1
        elif status == 'failed':
            self.failed += 1
        elif status == 'skipped':
            self.skipped += 1
    
    def get_progress(self) -> str:
        """
        Get progress string.
        
        Returns:
            Formatted progress string
        """
        processed = self.completed + self.failed + self.skipped
        percentage = (processed / self.total) * 100 if self.total > 0 else 0
        return f"Progress: {processed}/{self.total} ({percentage:.1f}%) - " \
               f"✓ {self.completed} ✗ {self.failed} ⊘ {self.skipped}"
