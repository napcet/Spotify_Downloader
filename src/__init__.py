"""
Spotify Music Downloader
A tool to download songs from Spotify playlists in various formats.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .spotify_client import SpotifyClient
from .downloader import Downloader
from .youtube_search import YouTubeSearcher
from .metadata import MetadataEmbedder
from .utils import load_config, setup_logging

# Optional imports
try:
    from .converter import AudioConverter
except ImportError:
    AudioConverter = None

__all__ = [
    'SpotifyClient',
    'Downloader',
    'YouTubeSearcher',
    'AudioConverter',
    'MetadataEmbedder',
    'load_config',
    'setup_logging'
]
