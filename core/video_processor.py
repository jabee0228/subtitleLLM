"""
Video Processor - Main processing orchestrator
Coordinates audio extraction, transcription, LLM correction, and subtitle generation
"""

import os
import sys
import logging
from typing import Optional, Dict, List

from .audio_extractor import AudioExtractor
from .whisper_transcriber import WhisperTranscriber
from .llm_corrector import LLMCorrector
from .subtitle_generator import SubtitleGenerator

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Main video processing coordinator"""

    def __init__(self,
                 whisper_model: str = "base",
                 llm_provider: str = "openai",
                 llm_api_key: Optional[str] = None):
        """
        Initialize video processor

        Args:
            whisper_model: Whisper model name
            llm_provider: LLM provider
            llm_api_key: LLM API key
        """
        self.audio_extractor = AudioExtractor()
        self.transcriber = WhisperTranscriber(whisper_model)
        self.corrector = LLMCorrector(llm_provider, llm_api_key)
        self.subtitle_generator = SubtitleGenerator()

        logger.info("Video processor initialization complete")

    def _write_segments_txt(self, segments: List[Dict], output_path: str) -> str:
        """Write plain text file with one segment per line."""
        try:
            lines = []
            for seg in segments:
                text = (seg.get('text') or '').strip()
                if text:
                    lines.append(text)
            content = "\n".join(lines)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Text file generated: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"Failed to write text file {output_path}: {str(e)}")
            return output_path

    def process_video(self,
                     video_path: str,
                     output_dir: Optional[str] = None,
                     language: str = "zh",
                     enable_correction: bool = True) -> Dict[str, str]:
        """
        Process video to generate subtitles

        Args:
            video_path: Video file path
            output_dir: Output directory (optional)
            language: Language code
            enable_correction: Whether to enable LLM correction

        Returns:
            Dict[str, str]: Dictionary containing file paths for each stage
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if output_dir is None:
            output_dir = os.path.dirname(video_path)

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        result_paths = {
            'video': video_path,
            'output_dir': output_dir
        }

        try:
            # Step 1: Extract audio
            logger.info("=== Step 1: Extract Audio ===")
            audio_path = os.path.join(output_dir, f"{base_name}.wav")
            audio_path = self.audio_extractor.extract_audio(video_path, audio_path)
            result_paths['audio'] = audio_path

            # Step 2: Speech to text
            logger.info("=== Step 2: Speech to Text ===")
            transcription = self.transcriber.transcribe_audio(audio_path, language)
            segments = self.transcriber.extract_segments(transcription)

            transcription_path = os.path.join(output_dir, f"{base_name}_transcription.json")
            self.transcriber.save_transcription(transcription, transcription_path)
            result_paths['transcription'] = transcription_path

            # Write pre-LLM plain text
            pre_txt_path = os.path.join(output_dir, f"{base_name}_pre_llm.txt")
            self._write_segments_txt(segments, pre_txt_path)
            result_paths['pre_llm_txt'] = pre_txt_path

            # Step 3: LLM correction (if enabled)
            if enable_correction:
                logger.info("=== Step 3: LLM Subtitle Correction ===")
                segments = self.corrector.correct_segments(segments, language=language)
            else:
                logger.info("=== Skip LLM Correction ===")

            # Write post-LLM plain text (will equal pre-LLM if correction skipped)
            post_txt_path = os.path.join(output_dir, f"{base_name}_post_llm.txt")
            self._write_segments_txt(segments, post_txt_path)
            result_paths['post_llm_txt'] = post_txt_path

            # Step 4: Generate SRT subtitles
            logger.info("=== Step 4: Generate SRT Subtitles ===")
            srt_path = os.path.join(output_dir, f"{base_name}.srt")
            srt_path = self.subtitle_generator.generate_srt(segments, srt_path)
            result_paths['srt'] = srt_path

            preview = self.subtitle_generator.preview_subtitles(segments)
            logger.info(f"\n{preview}")

            # Validate SRT file
            if self.subtitle_generator.validate_srt(srt_path):
                logger.info("✅ Subtitle generation complete!")
            else:
                logger.warning("⚠️ SRT file may have issues")

            return result_paths

        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            raise

    def get_video_info(self, video_path: str) -> Dict:
        """Get video information"""
        return self.audio_extractor.get_video_info(video_path)

    def cleanup_temp_files(self, result_paths: Dict[str, str], keep_audio: bool = False):
        """
        Clean up temporary files

        Args:
            result_paths: Processing result path dictionary
            keep_audio: Whether to keep audio file
        """
        files_to_remove = []

        if not keep_audio and 'audio' in result_paths:
            files_to_remove.append(result_paths['audio'])

        if 'transcription' in result_paths:
            files_to_remove.append(result_paths['transcription'])

        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {file_path}: {str(e)}")
