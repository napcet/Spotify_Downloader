"""
Deezer Client Module
Handles interaction with Deezer for downloading high-quality FLAC files.
"""

import requests
import json
from typing import Dict, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DeezerClient:
    """Client for interacting with Deezer API and downloading tracks."""
    
    # Deezer API endpoints
    API_BASE = "https://api.deezer.com"
    SEARCH_URL = f"{API_BASE}/search"
    TRACK_URL = f"{API_BASE}/track"
    
    def __init__(self, arl_token: Optional[str] = None):
        """
        Initialize Deezer client.
        
        Args:
            arl_token: Deezer ARL token for authentication (required for FLAC)
        """
        self.arl_token = arl_token
        self.session = requests.Session()
        
        if arl_token:
            self.session.cookies.set('arl', arl_token, domain='.deezer.com')
            logger.info("Deezer client initialized with ARL token")
        else:
            logger.warning("No ARL token provided - only preview quality available")
    
    def search_track(self, track: Dict) -> Optional[Dict]:
        """
        Search for a track on Deezer.
        
        Args:
            track: Track metadata from Spotify
            
        Returns:
            Deezer track information or None
        """
        try:
            # Build search query
            query = f"{track['artist']} {track['name']}"
            
            params = {
                'q': query,
                'limit': 10
            }
            
            response = self.session.get(self.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('data'):
                logger.warning(f"No Deezer results for: {query}")
                return None
            
            # Find best match
            best_match = self._find_best_match(track, data['data'])
            
            if best_match:
                logger.info(f"Found Deezer match: {best_match['title']} by {best_match['artist']['name']}")
                return best_match
            
            return None
        
        except Exception as e:
            logger.error(f"Deezer search failed: {e}")
            return None
    
    def _find_best_match(self, spotify_track: Dict, deezer_results: List[Dict]) -> Optional[Dict]:
        """
        Find the best matching Deezer track.
        
        Args:
            spotify_track: Spotify track metadata
            deezer_results: List of Deezer search results
            
        Returns:
            Best matching Deezer track or None
        """
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
            deezer_duration = result['duration']
            duration_diff = abs(spotify_duration - deezer_duration)
            if duration_diff <= 5:
                score += 20
            elif duration_diff <= 10:
                score += 10
            
            # Prefer explicit versions if Spotify track is explicit
            if spotify_track.get('explicit') and result.get('explicit_lyrics'):
                score += 10
            
            scored_results.append((score, result))
        
        # Sort by score and return best
        if scored_results:
            scored_results.sort(key=lambda x: x[0], reverse=True)
            best_score, best_result = scored_results[0]
            
            if best_score >= 60:  # Minimum confidence threshold
                return best_result
        
        return None
    
    def get_track_download_url(self, track_id: str, quality: str = 'FLAC') -> Optional[str]:
        """
        Get download URL for a Deezer track.
        
        Args:
            track_id: Deezer track ID
            quality: Quality level (MP3_128, MP3_320, FLAC)
            
        Returns:
            Download URL or None
        """
        if not self.arl_token and quality == 'FLAC':
            logger.error("FLAC downloads require ARL token")
            return None
        
        try:
            # Note: Direct download URL generation requires implementing
            # Deezer's download protocol which involves decryption
            # This is a placeholder - you'll need to use a library like deemix
            logger.info(f"Getting download URL for track {track_id} in {quality} quality")
            
            # For actual implementation, consider using:
            # - deemix library (https://gitlab.com/Bockiii/deemix-py)
            # - deezer-python with proper decryption
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            return None
    
    def download_track(self, deezer_track: Dict, output_path: str, quality: str = 'FLAC') -> bool:
        """
        Download a track from Deezer.
        
        Args:
            deezer_track: Deezer track information
            output_path: Output file path
            quality: Quality level
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This requires implementing Deezer's download and decryption protocol
            # For legal reasons, this is a placeholder
            logger.warning("Direct Deezer download requires proper implementation")
            logger.info("Consider using deemix library or API")
            return False
        
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    @staticmethod
    def validate_arl_token(arl_token: str) -> bool:
        """
        Validate Deezer ARL token.
        
        Args:
            arl_token: ARL token to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            session = requests.Session()
            session.cookies.set('arl', arl_token, domain='.deezer.com')
            
            response = session.get('https://www.deezer.com/ajax/gw-light.php', 
                                 params={'method': 'deezer.getUserData', 'api_version': '1.0'},
                                 timeout=10)
            
            data = response.json()
            return data.get('results', {}).get('USER', {}).get('USER_ID', 0) > 0
        
        except Exception:
            return False
