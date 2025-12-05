"""
Spotify Music Downloader
A tool to download songs from Spotify playlists in various formats.
"""

from .__version__ import (
    __version__,
    __version_info__,
    __title__,
    __description__,
    __author__,
    __license__,
    __url__
)

from .spotify_client import SpotifyClient
from .downloader import Downloader
from .youtube_search import YouTubeSearcher
from .metadata import MetadataEmbedder
from .utils import load_config, setup_logging

__all__ = [
    'SpotifyClient',
    'Downloader',
    'YouTubeSearcher',
    'MetadataEmbedder',
    'load_config',
    'setup_logging'
]
