"""
Subtitle Generator - Generate SRT subtitle files from transcribed and corrected text
"""

import os
import logging
import pysrt
import json
from typing import List, Dict
from datetime import timedelta

logger = logging.getLogger(__name__)

class SubtitleGenerator:
    """Generate SRT format subtitle files"""

    def __init__(self):
        self.max_chars_per_line = 32  # Maximum characters per line
        self.max_lines_per_subtitle = 2  # Maximum lines per subtitle

    def generate_srt(self, segments: List[Dict], output_path: str) -> str:
        """
        Generate SRT subtitle file

        Args:
            segments: List of subtitle segments
            output_path: Output SRT file path

        Returns:
            str: Path to generated SRT file
        """
        try:
            subs = pysrt.SubRipFile()

            for i, segment in enumerate(segments):
                text = segment.get('text', '').strip()
                if not text:
                    continue

                formatted_text = self._format_subtitle_text(text)
                start_time = self._seconds_to_srt_time(segment.get('start', 0))
                end_time = self._seconds_to_srt_time(segment.get('end', 0))

                subtitle_item = pysrt.SubRipItem(
                    index=i + 1,
                    start=start_time,
                    end=end_time,
                    text=formatted_text
                )

                subs.append(subtitle_item)

            # Save SRT file
            subs.save(output_path, encoding='utf-8')
            logger.info(f"SRT subtitle file generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate SRT file: {str(e)}")
            raise

    def _format_subtitle_text(self, text: str) -> str:
        """
        Format subtitle text with line breaks

        Args:
            text: Original text

        Returns:
            str: Formatted text
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= self.max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
                if len(lines) >= self.max_lines_per_subtitle:
                    break

        if current_line and len(lines) < self.max_lines_per_subtitle:
            lines.append(current_line)

        return "\n".join(lines)

    def _seconds_to_srt_time(self, seconds: float) -> pysrt.SubRipTime:
        """
        Convert seconds to SRT time format

        Args:
            seconds: Number of seconds

        Returns:
            pysrt.SubRipTime: SRT time object
        """
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = int((td.total_seconds() - total_seconds) * 1000)

        return pysrt.SubRipTime(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds
        )

    def preview_subtitles(self, segments: List[Dict], num_items: int = 5) -> str:
        """
        Generate subtitle preview

        Args:
            segments: List of subtitle segments
            num_items: Number of preview items

        Returns:
            str: Preview text
        """
        preview_lines = []
        preview_lines.append("=== Subtitle Preview ===")

        for i, segment in enumerate(segments[:num_items]):
            start = segment.get('start', 0)
            end = segment.get('end', 0)
            text = segment.get('text', '').strip()

            start_str = f"{int(start//60):02d}:{int(start%60):02d}"
            end_str = f"{int(end//60):02d}:{int(end%60):02d}"

            preview_lines.append(f"{i+1}. [{start_str} - {end_str}] {text}")

        if len(segments) > num_items:
            preview_lines.append(f"... and {len(segments) - num_items} more subtitle items")

        return "\n".join(preview_lines)

    def validate_srt(self, srt_path: str) -> bool:
        """
        Validate SRT file format

        Args:
            srt_path: SRT file path

        Returns:
            bool: Whether the file is valid
        """
        try:
            subs = pysrt.open(srt_path, encoding='utf-8')
            logger.info(f"SRT file validation successful, {len(subs)} subtitle items")
            return True

        except Exception as e:
            logger.error(f"SRT file validation failed: {str(e)}")
            return False
