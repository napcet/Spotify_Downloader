"""
Audio Converter Module
Handles audio format conversion and processing using FFmpeg.
"""

from pydub import AudioSegment
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AudioConverter:
    """Handles audio format conversion."""
    
    def __init__(self, config: dict):
        """
        Initialize audio converter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.audio_config = config.get('audio', {})
        self.sample_rate = self.audio_config.get('sample_rate', 48000)
        self.bitrate = self.audio_config.get('bitrate', 320)
        self.channels = self.audio_config.get('channels', 2)
    
    def convert(self, input_path: str, output_format: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Convert audio file to specified format.
        
        Args:
            input_path: Path to input audio file
            output_format: Target format (mp3, flac, wav, etc.)
            output_path: Optional output path (defaults to same as input with new extension)
            
        Returns:
            Path to converted file or None on failure
        """
        try:
            input_file = Path(input_path)
            
            if not input_file.exists():
                logger.error(f"Input file not found: {input_path}")
                return None
            
            # Determine output path
            if output_path is None:
                output_path = str(input_file.with_suffix(f'.{output_format}'))
            
            logger.info(f"Converting {input_path} to {output_format}")
            
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Apply audio settings
            if self.channels:
                audio = audio.set_channels(self.channels)
            if self.sample_rate:
                audio = audio.set_frame_rate(self.sample_rate)
            
            # Export with format-specific settings
            export_params = self._get_export_params(output_format)
            audio.export(output_path, format=output_format, **export_params)
            
            logger.info(f"Successfully converted to: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None
    
    def _get_export_params(self, output_format: str) -> dict:
        """
        Get format-specific export parameters.
        
        Args:
            output_format: Target audio format
            
        Returns:
            Dictionary of export parameters
        """
        params = {}
        
        if output_format == 'mp3':
            params['bitrate'] = f'{self.bitrate}k'
            params['parameters'] = ['-q:a', '0']  # Highest quality
        
        elif output_format == 'flac':
            params['parameters'] = ['-compression_level', '8']  # Maximum compression
        
        elif output_format == 'wav':
            params['parameters'] = ['-acodec', 'pcm_s16le']  # 16-bit PCM
        
        elif output_format == 'm4a':
            params['bitrate'] = f'{self.bitrate}k'
            params['codec'] = 'aac'
        
        elif output_format == 'opus':
            params['bitrate'] = f'{self.bitrate}k'
            params['codec'] = 'libopus'
        
        return params
    
    def normalize_audio(self, audio_path: str) -> bool:
        """
        Normalize audio volume.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            
            # Normalize to -20 dBFS
            change_in_dBFS = -20.0 - audio.dBFS
            normalized_audio = audio.apply_gain(change_in_dBFS)
            
            # Export back to same file
            normalized_audio.export(audio_path, format=Path(audio_path).suffix[1:])
            
            logger.info(f"Normalized audio: {audio_path}")
            return True
        
        except Exception as e:
            logger.error(f"Audio normalization failed: {e}")
            return False
    
    def trim_silence(self, audio_path: str, silence_thresh: int = -50) -> bool:
        """
        Trim silence from beginning and end of audio.
        
        Args:
            audio_path: Path to audio file
            silence_thresh: Silence threshold in dBFS
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from pydub.silence import detect_leading_silence
            
            audio = AudioSegment.from_file(audio_path)
            
            # Trim leading silence
            start_trim = detect_leading_silence(audio, silence_threshold=silence_thresh)
            
            # Trim trailing silence (reverse, detect, reverse back)
            end_trim = detect_leading_silence(audio.reverse(), silence_threshold=silence_thresh)
            
            # Calculate duration
            duration = len(audio)
            trimmed_audio = audio[start_trim:duration - end_trim]
            
            # Export
            trimmed_audio.export(audio_path, format=Path(audio_path).suffix[1:])
            
            logger.info(f"Trimmed silence from: {audio_path}")
            return True
        
        except Exception as e:
            logger.error(f"Silence trimming failed: {e}")
            return False
