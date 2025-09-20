"""
Utility Functions - Common utility functions for the subtitle generation system
"""

import os
import time
from typing import List, Dict
from datetime import datetime

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to readable time string

    Args:
        seconds: Number of seconds

    Returns:
        str: Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def validate_file_path(file_path: str, extensions: List[str] = None) -> bool:
    """
    Validate file path and extensions

    Args:
        file_path: File path
        extensions: List of allowed extensions

    Returns:
        bool: Whether the file is valid
    """
    if not os.path.exists(file_path):
        return False

    if extensions:
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in [ext.lower() for ext in extensions]

    return True

def create_output_filename(input_path: str, suffix: str, extension: str) -> str:
    """
    Create output filename based on input path

    Args:
        input_path: Input file path
        suffix: Suffix to add
        extension: New file extension

    Returns:
        str: Output file path
    """
    base_dir = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(base_dir, f"{base_name}_{suffix}.{extension}")

def estimate_processing_time(video_duration: float, model_size: str) -> float:
    """
    Estimate processing time based on video duration and model size

    Args:
        video_duration: Video duration in seconds
        model_size: Whisper model size

    Returns:
        float: Estimated processing time in seconds
    """
    time_factors = {
        "tiny": 0.1,
        "base": 0.2,
        "small": 0.4,
        "medium": 0.8,
        "large": 1.5
    }

    factor = time_factors.get(model_size, 0.5)
    return video_duration * factor

def log_processing_stats(start_time: float, video_duration: float, segments_count: int):
    """
    Log processing statistics

    Args:
        start_time: Processing start time
        video_duration: Video duration
        segments_count: Number of subtitle segments
    """
    processing_time = time.time() - start_time

    print(f"\n=== Processing Statistics ===")
    print(f"Video duration: {format_duration(video_duration)}")
    print(f"Processing time: {format_duration(processing_time)}")
    print(f"Subtitle segments: {segments_count}")
    print(f"Processing speed: {video_duration/processing_time:.1f}x realtime")
    print(f"Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

class ProgressTracker:
    """Progress tracking utility class"""

    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()

    def update(self, step_name: str):
        """Update progress with step name"""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        elapsed = time.time() - self.start_time

        print(f"\rProgress: {progress:.1f}% ({self.current_step}/{self.total_steps}) - {step_name}", end="", flush=True)

        if self.current_step == self.total_steps:
            print(f"\n✅ All steps completed in {elapsed:.1f} seconds")

    def finish(self):
        """Finish progress tracking"""
        if self.current_step < self.total_steps:
            print(f"\nProgress tracking ended")
