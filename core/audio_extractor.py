"""
Audio Extractor - Extract audio from video files
Uses MoviePy to extract audio in WAV format for Whisper processing
"""

import os
import logging
from moviepy import VideoFileClip
from typing import Optional

logger = logging.getLogger(__name__)

class AudioExtractor:
    """Extract audio from video files"""

    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']

    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video file

        Args:
            video_path: Video file path
            output_path: Output audio file path (optional)

        Returns:
            str: Path to extracted audio file

        Raises:
            FileNotFoundError: Video file not found
            ValueError: Unsupported video format
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        file_ext = os.path.splitext(video_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported video format: {file_ext}")

        if output_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_dir = os.path.dirname(video_path)
            output_path = os.path.join(output_dir, f"{base_name}.wav")

        try:
            logger.info(f"Starting audio extraction from {video_path}...")

            # Use MoviePy to extract audio
            video = VideoFileClip(video_path)
            audio = video.audio

            # Save as WAV format (well supported by Whisper)
            # Some moviepy versions do not support 'verbose' kwarg; pass only logger to silence output
            audio.write_audiofile(output_path, logger=None)

            audio.close()
            video.close()

            logger.info(f"Audio extraction complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Audio extraction failed: {str(e)}")
            raise

    def get_video_info(self, video_path: str) -> dict:
        """
        Get video information

        Args:
            video_path: Video file path

        Returns:
            dict: Dictionary containing video information
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            video = VideoFileClip(video_path)
            info = {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'filename': os.path.basename(video_path)
            }
            video.close()
            return info

        except Exception as e:
            logger.error(f"Failed to get video information: {str(e)}")
            raise
