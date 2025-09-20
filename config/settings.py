"""
Configuration Settings - Application configuration classes
"""

import os
import json
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any

@dataclass
class WhisperConfig:
    """Whisper configuration"""
    model_name: str = "base"  # tiny, base, small, medium, large
    language: Optional[str] = None      # Language code, None for auto-detect

@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "openai"  # openai or gemini
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"  # For OpenAI
    temperature: float = 0.3

@dataclass
class SubtitleConfig:
    """Subtitle configuration"""
    max_chars_per_line: int = 32
    max_lines_per_subtitle: int = 2
    output_format: str = "srt"  # srt, vtt, ass

@dataclass
class ProcessingConfig:
    """Processing configuration"""
    enable_llm_correction: bool = True
    keep_temp_files: bool = False
    keep_audio_file: bool = False
    output_dir: Optional[str] = None

@dataclass
class AppConfig:
    """Main application configuration with nested sections"""
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)

    def __post_init__(self):
        """Load environment variables after initialization"""
        self.load_from_env()

    # ---- Backward-compatible attribute aliases ----
    @property
    def whisper_model(self) -> str:
        return self.whisper.model_name

    @whisper_model.setter
    def whisper_model(self, value: str):
        self.whisper.model_name = value

    @property
    def language(self) -> Optional[str]:
        return self.whisper.language

    @language.setter
    def language(self, value: Optional[str]):
        self.whisper.language = value

    @property
    def llm_provider(self) -> str:
        return self.llm.provider

    @llm_provider.setter
    def llm_provider(self, value: str):
        self.llm.provider = value

    @property
    def api_key(self) -> Optional[str]:
        return self.llm.api_key

    @api_key.setter
    def api_key(self, value: Optional[str]):
        self.llm.api_key = value

    @property
    def enable_correction(self) -> bool:
        return self.processing.enable_llm_correction

    @enable_correction.setter
    def enable_correction(self, value: bool):
        self.processing.enable_llm_correction = value

    @property
    def output_dir(self) -> Optional[str]:
        return self.processing.output_dir

    @output_dir.setter
    def output_dir(self, value: Optional[str]):
        self.processing.output_dir = value

    # ---- Env loading ----
    def load_from_env(self):
        """Load configuration from environment variables"""
        # Prefer provider-specific keys; fall back to generic LLM_API_KEY
        if not self.llm.api_key:
            if self.llm.provider == "openai":
                self.llm.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
            elif self.llm.provider == "gemini":
                self.llm.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
            else:
                self.llm.api_key = os.getenv("LLM_API_KEY")

        # Optional language override
        env_lang = os.getenv("WHISPER_LANGUAGE")
        if env_lang:
            self.whisper.language = env_lang

    # ---- Serialization ----
    @classmethod
    def from_file(cls, file_path: str) -> 'AppConfig':
        """Load configuration from JSON file (supports nested and legacy flat formats)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)

            # If already nested
            if isinstance(data.get('whisper'), dict) or isinstance(data.get('llm'), dict):
                whisper_cfg = WhisperConfig(**data.get('whisper', {}))
                llm_cfg = LLMConfig(**data.get('llm', {}))
                subtitle_cfg = SubtitleConfig(**data.get('subtitle', {}))
                processing_cfg = ProcessingConfig(**data.get('processing', {}))
                cfg = cls(
                    whisper=whisper_cfg,
                    llm=llm_cfg,
                    subtitle=subtitle_cfg,
                    processing=processing_cfg
                )
            else:
                # Legacy flat keys mapping
                whisper_cfg = WhisperConfig(
                    model_name=data.get('whisper_model', WhisperConfig.model_name),
                    language=data.get('language')
                )
                llm_cfg = LLMConfig(
                    provider=data.get('llm_provider', LLMConfig.provider),
                    api_key=data.get('api_key') or data.get('llm_api_key')
                )
                processing_cfg = ProcessingConfig(
                    enable_llm_correction=data.get('enable_correction', ProcessingConfig.enable_llm_correction),
                    output_dir=data.get('output_dir')
                )
                subtitle_cfg = SubtitleConfig()
                cfg = cls(
                    whisper=whisper_cfg,
                    llm=llm_cfg,
                    subtitle=subtitle_cfg,
                    processing=processing_cfg
                )

            cfg.load_from_env()
            return cfg
        except Exception as e:
            print(f"Failed to load config from {file_path}: {e}")
            return cls()

    def to_file(self, file_path: str):
        """Save configuration to JSON file (nested structure)"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config to {file_path}: {e}")

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
