"""
SubtitleLLM - Main Program Entry Point
Automatic Video Subtitle Generation and Correction System
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.video_processor import VideoProcessor
from config.settings import AppConfig

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('subtitle_generation.log', encoding='utf-8')
        ]
    )

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Automatic Video Subtitle Generation and Correction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python main.py video.mp4                    # Basic usage
  python main.py video.mp4 -o ./output       # Specify output directory
  python main.py video.mp4 --no-correction   # Disable LLM correction
  python main.py video.mp4 --model small     # Use small model
  python main.py video.mp4 --lang en         # English subtitles
  python main.py video.mp4 --provider gemini # Use Gemini API
        """
    )

    # Required arguments
    parser.add_argument(
        "video_path",
        help="Video file path"
    )

    # Optional arguments
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: video directory)"
    )

    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )

    parser.add_argument(
        "--lang",
        default="zh",
        help="Language code (default: zh Chinese)"
    )

    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "gemini"],
        help="LLM provider (default: openai)"
    )

    parser.add_argument(
        "--no-correction",
        action="store_true",
        help="Disable LLM correction"
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files"
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Check if video file exists
        if not os.path.exists(args.video_path):
            logger.error(f"Video file not found: {args.video_path}")
            sys.exit(1)

        # Load configuration
        config = AppConfig()
        config.load_from_env()

        # Apply command line arguments
        config.whisper.model_name = args.model
        config.whisper.language = args.lang
        config.llm.provider = args.provider
        config.processing.enable_llm_correction = not args.no_correction
        config.processing.keep_temp_files = args.keep_temp

        logger.info("=== SubtitleLLM Automatic Subtitle Generation System ===")
        logger.info(f"Video file: {args.video_path}")
        logger.info(f"Whisper model: {config.whisper.model_name}")
        logger.info(f"Language: {config.whisper.language}")
        logger.info(f"LLM provider: {config.llm.provider}")
        logger.info(f"LLM correction: {'Enabled' if config.processing.enable_llm_correction else 'Disabled'}")

        # Check API key (if LLM correction is enabled)
        if config.processing.enable_llm_correction and not config.llm.api_key:
            logger.warning("LLM API key not found, disabling LLM correction")
            config.processing.enable_llm_correction = False

        # Initialize processor
        processor = VideoProcessor(
            whisper_model=config.whisper.model_name,
            llm_provider=config.llm.provider,
            llm_api_key=config.llm.api_key
        )

        # Get video information
        video_info = processor.get_video_info(args.video_path)
        logger.info(f"Video duration: {video_info['duration']:.1f} seconds")
        logger.info(f"Video size: {video_info['size']}")

        # Process video
        result_paths = processor.process_video(
            video_path=args.video_path,
            output_dir=args.output_dir,
            language=config.whisper.language,
            enable_correction=config.processing.enable_llm_correction
        )

        # Clean up temporary files
        if not config.processing.keep_temp_files:
            processor.cleanup_temp_files(result_paths, keep_audio=config.processing.keep_audio_file)

        # Display results
        logger.info("\n=== Processing Complete ===")
        logger.info(f"Subtitle file: {result_paths['srt']}")
        # New: print pre/post LLM text files
        logger.info(f"Pre-LLM text: {result_paths.get('pre_llm_txt', 'N/A')}")
        logger.info(f"Post-LLM text: {result_paths.get('post_llm_txt', 'N/A')}")

        if config.processing.keep_temp_files:
            logger.info(f"Audio file: {result_paths.get('audio', 'N/A')}")
            logger.info(f"Transcription file: {result_paths.get('transcription', 'N/A')}")

        logger.info("Subtitle generation successful!")

    except KeyboardInterrupt:
        logger.info("User interrupted operation")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
