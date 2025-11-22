"""
Multi-Source Download Manager
Manages downloading from multiple sources (Deezer, YouTube) with fallback.
"""

import logging
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class MultiSourceDownloader:
    """Manages downloading from multiple sources with priority and fallback."""
    
    def __init__(self, config: Dict):
        """
        Initialize multi-source downloader.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.sources = {}
        self.source_priority = config.get('download', {}).get('source_priority', ['deezer', 'youtube'])
        
        # Initialize available sources
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize all available download sources."""
        # Try to initialize Deezer/Deemix
        deezer_config = self.config.get('deezer', {})
        if deezer_config.get('enabled') and deezer_config.get('arl_token'):
            try:
                from .deemix_client import DeemixClient, DEEMIX_AVAILABLE
                
                if DEEMIX_AVAILABLE:
                    self.sources['deezer'] = DeemixClient(
                        deezer_config['arl_token'],
                        self.config
                    )
                    logger.info("✓ Deezer/Deemix source initialized (FLAC quality available)")
                else:
                    logger.warning("Deemix library not available. Install with: pip install deemix deezer-py")
            except Exception as e:
                logger.warning(f"Failed to initialize Deezer source: {e}")
        
        # Initialize YouTube downloader
        try:
            from .downloader import Downloader
            from .youtube_search import YouTubeSearcher
            
            self.sources['youtube'] = {
                'downloader': Downloader(self.config),
                'searcher': YouTubeSearcher(self.config)
            }
            logger.info("✓ YouTube source initialized")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube source: {e}")
    
    def download(self, track: Dict, progress_callback=None) -> Optional[str]:
        """
        Download track from best available source.
        
        Args:
            track: Track metadata from Spotify
            progress_callback: Optional progress callback
            
        Returns:
            Path to downloaded file or None
        """
        # Try each source in priority order
        for source in self.source_priority:
            if source not in self.sources:
                continue
            
            try:
                logger.info(f"Attempting download from {source.upper()}")
                
                if source == 'deezer':
                    result = self._download_from_deezer(track)
                elif source == 'youtube':
                    result = self._download_from_youtube(track, progress_callback)
                else:
                    continue
                
                if result:
                    logger.info(f"✓ Successfully downloaded from {source.upper()}")
                    return result
                else:
                    logger.warning(f"✗ Download from {source.upper()} failed, trying next source...")
            
            except Exception as e:
                logger.error(f"Error downloading from {source}: {e}")
                continue
        
        logger.error(f"Failed to download from all sources: {track['artist']} - {track['name']}")
        return None
    
    def _download_from_deezer(self, track: Dict) -> Optional[str]:
        """
        Download from Deezer.
        
        Args:
            track: Track metadata
            
        Returns:
            Path to downloaded file or None
        """
        try:
            deemix_client = self.sources.get('deezer')
            if not deemix_client:
                return None
            
            # Search for track on Deezer
            deezer_track = deemix_client.search_track(track)
            if not deezer_track:
                logger.warning("Track not found on Deezer")
                return None
            
            # Download
            output_dir = self.config.get('download', {}).get('output_dir', './downloads')
            output_path = deemix_client.download_track(deezer_track, output_dir)
            
            return output_path
        
        except Exception as e:
            logger.error(f"Deezer download error: {e}")
            return None
    
    def _download_from_youtube(self, track: Dict, progress_callback=None) -> Optional[str]:
        """
        Download from YouTube.
        
        Args:
            track: Track metadata
            progress_callback: Optional progress callback
            
        Returns:
            Path to downloaded file or None
        """
        try:
            youtube = self.sources.get('youtube')
            if not youtube:
                return None
            
            searcher = youtube['searcher']
            downloader = youtube['downloader']
            
            # Search for track on YouTube
            youtube_url = searcher.search(track)
            if not youtube_url:
                logger.warning("Track not found on YouTube")
                return None
            
            # Download
            output_path = downloader.download(youtube_url, track, progress_callback)
            
            return output_path
        
        except Exception as e:
            logger.error(f"YouTube download error: {e}")
            return None
    
    def get_available_sources(self) -> List[str]:
        """
        Get list of available sources.
        
        Returns:
            List of available source names
        """
        return list(self.sources.keys())
    
    def is_source_available(self, source: str) -> bool:
        """
        Check if a source is available.
        
        Args:
            source: Source name
            
        Returns:
            True if available, False otherwise
        """
        return source in self.sources
