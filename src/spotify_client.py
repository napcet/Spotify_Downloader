"""
Spotify API Client
Handles authentication and data retrieval from Spotify API.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Client for interacting with Spotify API."""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Spotify client.
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.sp = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Spotify API."""
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Successfully authenticated with Spotify API")
        except Exception as e:
            logger.error(f"Failed to authenticate with Spotify: {e}")
            raise
    
    def get_playlist_tracks(self, playlist_url: str) -> List[Dict]:
        """
        Get all tracks from a Spotify playlist.
        
        Args:
            playlist_url: Spotify playlist URL or URI
            
        Returns:
            List of track dictionaries
        """
        try:
            playlist_id = self._extract_id(playlist_url)
            tracks = []
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    track = item['track']
                    if track:  # Sometimes track can be None
                        tracks.append(self._format_track(track))
                
                # Handle pagination
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            logger.info(f"Retrieved {len(tracks)} tracks from playlist")
            return tracks
        
        except Exception as e:
            logger.error(f"Failed to get playlist tracks: {e}")
            raise
    
    def get_track(self, track_url: str) -> Dict:
        """
        Get a single track information.
        
        Args:
            track_url: Spotify track URL or URI
            
        Returns:
            Track dictionary
        """
        try:
            track_id = self._extract_id(track_url)
            track = self.sp.track(track_id)
            return self._format_track(track)
        except Exception as e:
            logger.error(f"Failed to get track: {e}")
            raise
    
    def get_album_tracks(self, album_url: str) -> List[Dict]:
        """
        Get all tracks from a Spotify album.
        
        Args:
            album_url: Spotify album URL or URI
            
        Returns:
            List of track dictionaries
        """
        try:
            album_id = self._extract_id(album_url)
            album = self.sp.album(album_id)
            tracks = []
            
            for track in album['tracks']['items']:
                # Album tracks don't have full info, so fetch each track
                full_track = self.sp.track(track['id'])
                tracks.append(self._format_track(full_track))
            
            logger.info(f"Retrieved {len(tracks)} tracks from album")
            return tracks
        
        except Exception as e:
            logger.error(f"Failed to get album tracks: {e}")
            raise
    
    def search_track(self, query: str) -> Optional[Dict]:
        """
        Search for a track.
        
        Args:
            query: Search query
            
        Returns:
            Track dictionary or None
        """
        try:
            results = self.sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                return self._format_track(results['tracks']['items'][0])
            return None
        except Exception as e:
            logger.error(f"Failed to search track: {e}")
            return None
    
    def _format_track(self, track: Dict) -> Dict:
        """
        Format track data into a standardized dictionary.
        
        Args:
            track: Raw track data from Spotify API
            
        Returns:
            Formatted track dictionary
        """
        return {
            'id': track['id'],
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'album_artist': track['album']['artists'][0]['name'],
            'release_date': track['album']['release_date'],
            'duration_ms': track['duration_ms'],
            'track_number': track['track_number'],
            'disc_number': track.get('disc_number', 1),
            'isrc': track.get('external_ids', {}).get('isrc'),
            'popularity': track.get('popularity', 0),
            'explicit': track.get('explicit', False),
            'artwork_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'spotify_url': track['external_urls']['spotify']
        }
    
    @staticmethod
    def _extract_id(url: str) -> str:
        """
        Extract Spotify ID from URL or URI.
        
        Args:
            url: Spotify URL or URI
            
        Returns:
            Spotify ID
        """
        if 'spotify.com' in url:
            # Extract from URL: https://open.spotify.com/playlist/xxxxx
            return url.split('/')[-1].split('?')[0]
        elif 'spotify:' in url:
            # Extract from URI: spotify:playlist:xxxxx
            return url.split(':')[-1]
        else:
            # Assume it's already an ID
            return url
