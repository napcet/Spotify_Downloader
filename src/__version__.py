"""
Version information for Spotify Downloader.
This is the single source of truth for version information.
"""

from pathlib import Path

__version__ = "1.0.1"
__version_info__ = tuple(int(x) for x in __version__.split("."))

# Read version from VERSION file if it exists
_version_file = Path(__file__).parent.parent / "VERSION"
if _version_file.exists():
    __version__ = _version_file.read_text().strip()
    __version_info__ = tuple(int(x) for x in __version__.split("."))

__title__ = "Spotify Music Downloader"
__description__ = "Download Spotify playlists, albums, and tracks in FLAC/MP3 format from free sources"
__author__ = "Mokshit Bindal"
__license__ = "MIT"
__url__ = "https://github.com/MokshitBindal/Spotify_Downloader"

# Version banner
_title_line = f"{__title__} v{__version__}"
_desc_line = "Download playlists in various formats"
VERSION_BANNER = f"""
╔═══════════════════════════════════════════════════════╗
║{_title_line:^55}║
║{_desc_line:^55}║
╚═══════════════════════════════════════════════════════╝
"""
