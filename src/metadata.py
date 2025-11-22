"""
Metadata Embedder Module
Handles embedding metadata and artwork into audio files.
"""

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC, TPE2, TCON
from pathlib import Path
from typing import Dict, Optional
import requests
import logging

logger = logging.getLogger(__name__)


class MetadataEmbedder:
    """Embeds metadata and artwork into audio files."""
    
    def __init__(self, config: Dict):
        """
        Initialize metadata embedder.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.metadata_config = config.get('metadata', {})
        self.embed_metadata = self.metadata_config.get('embed_metadata', True)
        self.embed_artwork = self.metadata_config.get('embed_artwork', True)
        self.embed_lyrics = self.metadata_config.get('embed_lyrics', False)
    
    def embed(self, audio_path: str, track: Dict) -> bool:
        """
        Embed metadata into audio file.
        
        Args:
            audio_path: Path to audio file
            track: Track metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.embed_metadata:
            return True
        
        try:
            file_path = Path(audio_path)
            file_extension = file_path.suffix.lower()
            
            logger.info(f"Embedding metadata for: {audio_path}")
            
            # Route to appropriate handler based on format
            if file_extension == '.mp3':
                return self._embed_mp3(audio_path, track)
            elif file_extension == '.flac':
                return self._embed_flac(audio_path, track)
            elif file_extension == '.m4a':
                return self._embed_m4a(audio_path, track)
            elif file_extension == '.wav':
                return self._embed_wav(audio_path, track)
            else:
                logger.warning(f"Unsupported format for metadata: {file_extension}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to embed metadata: {e}")
            return False
    
    def _embed_mp3(self, audio_path: str, track: Dict) -> bool:
        """Embed metadata into MP3 file."""
        try:
            audio = MP3(audio_path, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            try:
                audio.add_tags()
            except:
                pass
            
            # Basic metadata
            audio.tags.add(TIT2(encoding=3, text=track['name']))
            audio.tags.add(TPE1(encoding=3, text=track['artist']))
            audio.tags.add(TALB(encoding=3, text=track['album']))
            audio.tags.add(TPE2(encoding=3, text=track['album_artist']))
            audio.tags.add(TDRC(encoding=3, text=track['release_date'][:4]))  # Year only
            audio.tags.add(TRCK(encoding=3, text=str(track['track_number'])))
            
            # Add genre if available
            if 'genre' in track:
                audio.tags.add(TCON(encoding=3, text=track['genre']))
            
            # Embed artwork
            if self.embed_artwork and track.get('artwork_url'):
                artwork_data = self._download_artwork(track['artwork_url'])
                if artwork_data:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=artwork_data
                        )
                    )
            
            audio.save()
            logger.info(f"Successfully embedded MP3 metadata")
            return True
        
        except Exception as e:
            logger.error(f"MP3 metadata embedding failed: {e}")
            return False
    
    def _embed_flac(self, audio_path: str, track: Dict) -> bool:
        """Embed metadata into FLAC file."""
        try:
            audio = FLAC(audio_path)
            
            # Basic metadata
            audio['title'] = track['name']
            audio['artist'] = track['artist']
            audio['album'] = track['album']
            audio['albumartist'] = track['album_artist']
            audio['date'] = track['release_date'][:4]
            audio['tracknumber'] = str(track['track_number'])
            audio['discnumber'] = str(track.get('disc_number', 1))
            
            # Add additional metadata
            if track.get('isrc'):
                audio['isrc'] = track['isrc']
            if 'genre' in track:
                audio['genre'] = track['genre']
            
            # Embed artwork
            if self.embed_artwork and track.get('artwork_url'):
                artwork_data = self._download_artwork(track['artwork_url'])
                if artwork_data:
                    from mutagen.flac import Picture
                    import base64
                    
                    picture = Picture()
                    picture.type = 3  # Cover (front)
                    picture.mime = 'image/jpeg'
                    picture.desc = 'Cover'
                    picture.data = artwork_data
                    
                    audio.add_picture(picture)
            
            audio.save()
            logger.info(f"Successfully embedded FLAC metadata")
            return True
        
        except Exception as e:
            logger.error(f"FLAC metadata embedding failed: {e}")
            return False
    
    def _embed_m4a(self, audio_path: str, track: Dict) -> bool:
        """Embed metadata into M4A file."""
        try:
            audio = MP4(audio_path)
            
            # Basic metadata
            audio['\xa9nam'] = track['name']
            audio['\xa9ART'] = track['artist']
            audio['\xa9alb'] = track['album']
            audio['aART'] = track['album_artist']
            audio['\xa9day'] = track['release_date'][:4]
            audio['trkn'] = [(track['track_number'], 0)]
            audio['disk'] = [(track.get('disc_number', 1), 0)]
            
            # Embed artwork
            if self.embed_artwork and track.get('artwork_url'):
                artwork_data = self._download_artwork(track['artwork_url'])
                if artwork_data:
                    from mutagen.mp4 import MP4Cover
                    audio['covr'] = [MP4Cover(artwork_data, imageformat=MP4Cover.FORMAT_JPEG)]
            
            audio.save()
            logger.info(f"Successfully embedded M4A metadata")
            return True
        
        except Exception as e:
            logger.error(f"M4A metadata embedding failed: {e}")
            return False
    
    def _embed_wav(self, audio_path: str, track: Dict) -> bool:
        """Embed metadata into WAV file."""
        try:
            audio = WAVE(audio_path)
            
            # Add ID3 tag if it doesn't exist
            try:
                audio.add_tags()
            except:
                pass
            
            # WAV files use ID3 tags
            audio.tags.add(TIT2(encoding=3, text=track['name']))
            audio.tags.add(TPE1(encoding=3, text=track['artist']))
            audio.tags.add(TALB(encoding=3, text=track['album']))
            audio.tags.add(TDRC(encoding=3, text=track['release_date'][:4]))
            
            audio.save()
            logger.info(f"Successfully embedded WAV metadata")
            return True
        
        except Exception as e:
            logger.error(f"WAV metadata embedding failed: {e}")
            return False
    
    def _download_artwork(self, url: str) -> Optional[bytes]:
        """
        Download artwork from URL.
        
        Args:
            url: Artwork URL
            
        Returns:
            Artwork data as bytes or None
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download artwork: {e}")
            return None
