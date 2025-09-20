"""
Basic functionality tests
"""

import unittest
import os
import tempfile
from core.audio_extractor import AudioExtractor
from core.subtitle_generator import SubtitleGenerator

class TestAudioExtractor(unittest.TestCase):
    """Test audio extractor"""

    def setUp(self):
        self.extractor = AudioExtractor()

    def test_supported_formats(self):
        """Test supported formats"""
        expected_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        self.assertEqual(self.extractor.supported_formats, expected_formats)

    def test_file_not_found(self):
        """Test file not found scenario"""
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract_audio("non_existent_file.mp4")

class TestSubtitleGenerator(unittest.TestCase):
    """Test subtitle generator"""

    def setUp(self):
        self.generator = SubtitleGenerator()

    def test_format_subtitle_text(self):
        """Test subtitle text formatting"""
        long_text = "This is a very long text that needs to be split into multiple lines to fit subtitle display requirements"
        formatted = self.generator._format_subtitle_text(long_text)
        lines = formatted.split('\n')

        # Check that each line doesn't exceed the limit
        for line in lines:
            self.assertLessEqual(len(line), self.generator.max_chars_per_line)

        # Check that number of lines doesn't exceed the limit
        self.assertLessEqual(len(lines), self.generator.max_lines_per_subtitle)

    def test_seconds_to_srt_time(self):
        """Test time format conversion"""
        # Test 1 minute 30 seconds 500 milliseconds
        time_obj = self.generator._seconds_to_srt_time(90.5)
        self.assertEqual(time_obj.minutes, 1)
        self.assertEqual(time_obj.seconds, 30)
        self.assertEqual(time_obj.milliseconds, 500)

if __name__ == '__main__':
    unittest.main()
