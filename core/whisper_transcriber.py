"""
Whisper Transcriber - Convert audio to text using OpenAI Whisper
"""

import os
import json
import logging
import whisper
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """Use Whisper model for speech-to-text conversion"""

    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper transcriber

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        self.load_model()

    def load_model(self):
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise

    def transcribe_audio(self, audio_path: str, language: str = "zh") -> Dict:
        """
        Transcribe audio to text

        Args:
            audio_path: Audio file path
            language: Language code (zh, en, ja, etc.)

        Returns:
            Dict: Dictionary containing transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.model is None:
            raise RuntimeError("Whisper model not loaded")

        try:
            logger.info(f"Starting audio transcription: {audio_path}")

            # Use Whisper for transcription
            result = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True,
                verbose=False
            )

            logger.info(f"Transcription complete, {len(result['segments'])} segments")
            return result

        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            raise

    def extract_segments(self, transcription_result: Dict) -> List[Dict]:
        """
        Extract segment information from transcription results

        Args:
            transcription_result: Whisper transcription results

        Returns:
            List[Dict]: List of segment information
        """
        segments = []

        for segment in transcription_result.get('segments', []):
            segment_info = {
                'start': segment.get('start', 0),
                'end': segment.get('end', 0),
                'text': segment.get('text', '').strip(),
                'id': segment.get('id', 0)
            }
            segments.append(segment_info)

        return segments

    def save_transcription(self, transcription_result: Dict, output_path: str):
        """
        Save transcription results to JSON file

        Args:
            transcription_result: Transcription results
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcription_result, f, ensure_ascii=False, indent=2)
            logger.info(f"Transcription results saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save transcription results: {str(e)}")
            raise
