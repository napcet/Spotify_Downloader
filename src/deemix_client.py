"""
Deemix Integration Module
Uses the deemix library to download FLAC files from Deezer.
"""

import logging
from typing import Dict, Optional
from pathlib import Path

try:
    from deemix import generateDownloadObject
    from deemix.downloader import Downloader as DeemixDownloader
    from deemix.settings import load as loadSettings
    from deezer import Deezer
    DEEMIX_AVAILABLE = True
except ImportError:
    DEEMIX_AVAILABLE = False

logger = logging.getLogger(__name__)


class DeemixClient:
    """Client for downloading FLAC files using deemix."""
    
    def __init__(self, arl_token: str, config: Dict):
        """
        Initialize Deemix client.
        
        Args:
            arl_token: Deezer ARL token
            config: Configuration dictionary
        """
        if not DEEMIX_AVAILABLE:
            raise ImportError("deemix library not installed. Install with: pip install deemix")
        
        self.arl_token = arl_token
        self.config = config
        self.dz = Deezer()
        
        # Login to Deezer
        if not self.dz.login_via_arl(arl_token):
            raise ValueError("Invalid ARL token")
        
        # Load deemix settings
        self.settings = loadSettings()
        self._configure_settings()
        
        logger.info("Deemix client initialized successfully")
    
    def _configure_settings(self):
        """Configure deemix settings based on config."""
        download_config = self.config.get('download', {})
        audio_format = download_config.get('audio_format', 'flac')
        
        # Map format to deemix quality
        quality_map = {
            'mp3': '3',    # MP3 320kbps
            'flac': '9',   # FLAC
            'm4a': '3',    # MP3 320kbps (will be converted)
        }
        
        self.settings['downloadLocation'] = download_config.get('output_dir', './downloads')
        self.settings['maxBitrate'] = quality_map.get(audio_format, '9')
        self.settings['syncedLyrics'] = self.config.get('metadata', {}).get('embed_lyrics', False)
        self.settings['coverImageTemplate'] = 'folder'
        self.settings['saveArtwork'] = self.config.get('metadata', {}).get('embed_artwork', True)
        self.settings['embeddedArtworkSize'] = 1200
        self.settings['jpegImageQuality'] = 95
        self.settings['createM3UFile'] = False
        self.settings['executeCommand'] = ""
        self.settings['tags']['title'] = True
        self.settings['tags']['artist'] = True
        self.settings['tags']['album'] = True
        self.settings['tags']['year'] = True
        self.settings['tags']['tracknumber'] = True
        self.settings['tags']['discnumber'] = True
        self.settings['tags']['isrc'] = True
    
    def search_track(self, track: Dict) -> Optional[Dict]:
        """
        Search for a track on Deezer.
        
        Args:
            track: Track metadata from Spotify
            
        Returns:
            Deezer track information or None
        """
        try:
            query = f"{track['artist']} {track['name']}"
            results = self.dz.api.search_track(query, limit=10)
            
            if not results:
                logger.warning(f"No Deezer results for: {query}")
                return None
            
            # Find best match
            best_match = self._find_best_match(track, results)
            return best_match
        
        except Exception as e:
            logger.error(f"Deezer search failed: {e}")
            return None
    
    def _find_best_match(self, spotify_track: Dict, deezer_results: list) -> Optional[Dict]:
        """Find the best matching Deezer track."""
        spotify_name = spotify_track['name'].lower()
        spotify_artist = spotify_track['artist'].lower()
        spotify_duration = spotify_track['duration_ms'] / 1000
        
        scored_results = []
        
        for result in deezer_results:
            score = 0
            
            # Check title match
            deezer_title = result['title'].lower()
            if spotify_name == deezer_title:
                score += 50
            elif spotify_name in deezer_title or deezer_title in spotify_name:
                score += 30
            
            # Check artist match
            deezer_artist = result['artist']['name'].lower()
            if spotify_artist == deezer_artist:
                score += 50
            elif spotify_artist in deezer_artist or deezer_artist in spotify_artist:
                score += 30
            
            # Check duration (within 5 seconds)
            duration_diff = abs(spotify_duration - result['duration'])
            if duration_diff <= 5:
                score += 20
            
            scored_results.append((score, result))
        
        if scored_results:
            scored_results.sort(key=lambda x: x[0], reverse=True)
            best_score, best_result = scored_results[0]
            
            if best_score >= 60:
                return best_result
        
        return None
    
    def download_track(self, deezer_track: Dict, output_dir: str) -> Optional[str]:
        """
        Download a track from Deezer.
        
        Args:
            deezer_track: Deezer track information
            output_dir: Output directory
            
        Returns:
            Path to downloaded file or None
        """
        try:
            track_id = deezer_track['id']
            logger.info(f"Downloading from Deezer: {deezer_track['title']} by {deezer_track['artist']['name']}")
            
            # Generate download object
            download_obj = generateDownloadObject(self.dz, f"https://www.deezer.com/track/{track_id}", self.settings['maxBitrate'])
            
            # Create downloader
            downloader = DeemixDownloader(self.dz, download_obj, self.settings)
            
            # Download
            downloader.start()
            
            # Get output file path
            output_file = self._get_output_path(deezer_track, output_dir)
            
            if output_file and output_file.exists():
                logger.info(f"Successfully downloaded: {output_file}")
                return str(output_file)
            
            logger.error("Download completed but file not found")
            return None
        
        except Exception as e:
            logger.error(f"Deemix download failed: {e}")
            return None
    
    def _get_output_path(self, deezer_track: Dict, output_dir: str) -> Optional[Path]:
        """Get the output file path for a downloaded track."""
        # This is simplified - actual path depends on deemix settings
        artist = deezer_track['artist']['name']
        album = deezer_track['album']['title']
        title = deezer_track['title']
        
        # Sanitize filenames
        artist = self._sanitize_filename(artist)
        album = self._sanitize_filename(album)
        title = self._sanitize_filename(title)
        
        output_path = Path(output_dir) / artist / album / f"{title}.flac"
        return output_path if output_path.exists() else None
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip('. ')
