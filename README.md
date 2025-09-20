# SubtitleLLM
An intelligent automatic video subtitle generation system that combines OpenAI Whisper speech recognition with LLM correction for high-quality subtitle creation.

## Features

- **Automatic Audio Extraction**: Extract audio from various video formats (MP4, AVI, MOV, MKV, WMV, FLV)
- **Speech Recognition**: Convert speech to text using OpenAI Whisper models
- **AI-Powered Correction**: Improve transcription accuracy using LLM correction (OpenAI GPT or Google Gemini)
- **Multiple Output Formats**: Generate SRT subtitle files with proper timing
- **Multi-language Support**: Support for various languages with automatic detection
- **Flexible Configuration**: Customizable settings for different use cases
- **Command Line Interface**: Easy-to-use CLI with extensive options


## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd subtitleLLM
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy  `.env.example` to `.env` file):
```bash
# For OpenAI (optional, for LLM correction)
OPENAI_API_KEY=your_openai_api_key

# For Google Gemini (optional, alternative to OpenAI)
GEMINI_API_KEY=your_gemini_api_key
```

## Requirements

- Python 3.8+
- FFmpeg (for audio processing)
- GPU support recommended for larger Whisper models

### Dependencies

- `openai-whisper`: Speech recognition
- `openai`: GPT API access
- `google-generativeai`: Gemini API access
- `ffmpeg-python`: Audio processing
- `moviepy`: Video file handling
- `python-dotenv`: Environment variable management

## Usage

### Basic Usage

```bash
python main.py video.mp4
```

### Advanced Usage Examples

```bash
# Specify output directory
python main.py video.mp4 -o ./output

# Disable LLM correction (faster processing)
python main.py video.mp4 --no-correction

# Use different Whisper model
python main.py video.mp4 --model small

# Generate English subtitles
python main.py video.mp4 --lang en

# Use Google Gemini instead of OpenAI
python main.py video.mp4 --provider gemini

# Keep temporary files for debugging
python main.py video.mp4 --keep-temp

# Enable debug logging
python main.py video.mp4 --log-level DEBUG
```

### Command Line Options

- `video_path`: Path to input video file (required)
- `-o, --output-dir`: Output directory (default: same as video directory)
- `--model`: Whisper model size - tiny, base, small, medium, large (default: base)
- `--lang`: Language code (default: zh for Chinese)
- `--provider`: LLM provider - openai, gemini (default: openai)
- `--no-correction`: Disable LLM correction
- `--keep-temp`: Keep temporary files
- `--log-level`: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)

## Configuration

The system uses a hierarchical configuration system with support for environment variables and command-line overrides.

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `GEMINI_API_KEY`: Google Gemini API key
- `WHISPER_MODEL`: Default Whisper model name
- `DEFAULT_LANGUAGE`: Default language for transcription

### Configuration Classes

The application uses structured configuration with the following sections:

- **WhisperConfig**: Whisper model and language settings
- **LLMConfig**: LLM provider, API keys, and model parameters
- **SubtitleConfig**: Subtitle formatting options
- **ProcessingConfig**: Processing pipeline settings


## Supported Languages

The system supports all languages supported by OpenAI Whisper, including:

- English 
- Chinese 

## Performance Considerations

### Whisper Model Selection

- **tiny**: Fastest, lowest accuracy (~39 MB)
- **base**: Good balance of speed and accuracy (~74 MB)
- **small**: Better accuracy, slower (~244 MB)
- **medium**: High accuracy (~769 MB)
- **large**: Best accuracy, slowest (~1550 MB)

### LLM Correction

- Improves transcription accuracy significantly
- Adds processing time and API costs
- Can be disabled with `--no-correction` for faster processing



## Development

### Project Structure

```
subtitleLLM/
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration classes
├── core/
│   ├── __init__.py
│   ├── audio_extractor.py # Audio extraction
│   ├── whisper_transcriber.py # Speech recognition
│   ├── llm_corrector.py   # LLM correction
│   ├── subtitle_generator.py # Subtitle generation
│   └── video_processor.py # Main coordinator
├── tests/
│   ├── __init__.py
│   └── test_basic.py      # Basic tests
└── utils/
    └── __init__.py
```

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.


