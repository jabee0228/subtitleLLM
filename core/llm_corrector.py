"""
LLM Corrector - Correct subtitle errors using Large Language Models
Supports OpenAI GPT and Google Gemini
"""

import os
import logging
import openai
import google.generativeai as genai
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CorrectionResult:
    """Data class for correction results"""
    original_text: str
    corrected_text: str
    confidence: float
    corrections_made: List[str]

class LLMCorrector:
    """Use LLM to correct subtitle text"""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Initialize LLM corrector

        Args:
            provider: LLM provider ("openai" or "gemini")
            api_key: API key
        """
        self.provider = provider.lower()
        # Prefer explicitly provided api_key; fall back to env
        self.api_key = self._get_api_key()
        self._setup_client()

    def _get_api_key(self) -> str:
        """Get API key from environment variables"""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _setup_client(self):
        """Setup API client"""
        if not self.api_key:
            raise ValueError(f"Cannot find {self.provider.upper()} API key")

        if self.provider == "openai":
            openai.api_key = self.api_key
        elif self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def correct_text(self, text: str, context: str = "", language: str = "zh") -> CorrectionResult:
        """
        Correct text using LLM

        Args:
            text: Text to be corrected
            context: Context information
            language: ISO language code (e.g., zh, en). Controls prompt.

        Returns:
            CorrectionResult: Correction results
        """
        prompt = self._build_correction_prompt(text, context, language)

        try:
            if self.provider == "openai":
                corrected = self._correct_with_openai(prompt)
            elif self.provider == "gemini":
                corrected = self._correct_with_gemini(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            return self._parse_correction_result(text, corrected)

        except Exception as e:
            logger.error(f"Text correction failed: {str(e)}")
            return CorrectionResult(
                original_text=text,
                corrected_text=text,
                confidence=0.0,
                corrections_made=[]
            )

    def _build_correction_prompt(self, text: str, context: str = "", language: str = "zh") -> str:
        """Build correction prompt based on language"""
        lang = (language or "").lower()

        if lang.startswith("zh"):
            # Chinese-focused prompt (Simplified by default)
            base_prompt = f"""
你是專業的字幕校對助手。
目標語言：中文。
任務：
1) 修正常見同音字/錯別字（如：的/地/得，著/着，因/應 等）。
2) 修正標點（中英文括號、逗號、句號、問號、省略號等），優先使用中文標點。
3) 改善語法與流暢度，保留原意與口語風格，不過度改寫。
4) 僅在明顯為語音識別錯誤時移除口頭贅詞（呃、嗯等）。
5) 保留專有名詞與外文詞彙，不隨意翻譯或改名。
6) 僅返回「校正後文字」，不輸出任何解釋。

原文：{text}
{f"上下文：{context}" if context else ""}

校正後："""
        elif lang.startswith("en"):
            # English-focused prompt
            base_prompt = f"""
You are a professional subtitle proofreader.
Target language: English.
Tasks:
1) Fix homophones and common ASR errors (e.g., your/you're, its/it's).
2) Correct punctuation and capitalization.
3) Improve grammar and readability while preserving original meaning and speaker intent.
4) Remove filler words only if they are obvious ASR artifacts.
5) Keep proper nouns and foreign words, do not translate names.
6) Return only the corrected text without any explanation.

Original: {text}
{f"Context: {context}" if context else ""}

Corrected:"""
        else:
            # Generic prompt with target language hint
            base_prompt = f"""
You are a subtitle proofreader.
Target language: {language}.
Tasks:
1) Fix homophones and common ASR errors.
2) Correct punctuation and grammar appropriate for the target language.
3) Preserve original meaning and tone; avoid over-editing.
4) Keep proper nouns; do not translate names.
5) Return only the corrected text without any explanation.

Original: {text}
{f"Context: {context}" if context else ""}

Corrected:"""
        return base_prompt

    def _correct_with_openai(self, prompt: str) -> str:
        """Correct using OpenAI API"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional text correction assistant, specializing in correcting speech-to-text errors."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def _correct_with_gemini(self, prompt: str) -> str:
        """Correct using Gemini API"""
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def _parse_correction_result(self, original: str, corrected: str) -> CorrectionResult:
        """Parse correction results"""
        corrections_made = []
        if original != corrected:
            corrections_made.append(f"{original} -> {corrected}")

        confidence = 0.8 if corrections_made else 1.0

        return CorrectionResult(
            original_text=original,
            corrected_text=corrected,
            confidence=confidence,
            corrections_made=corrections_made
        )

    def correct_segments(self, segments: List[Dict], language: str = "zh") -> List[Dict]:
        """
        Correct subtitle segments

        Args:
            segments: List of subtitle segments
            language: ISO language code to guide prompts

        Returns:
            List[Dict]: List of corrected segments
        """
        corrected_segments = []

        for i, segment in enumerate(segments):
            text = segment.get('text', '')

            # Build context from previous and next segments
            context_parts = []
            if i > 0:
                context_parts.append(f"Previous: {segments[i-1].get('text', '')}")
            if i < len(segments) - 1:
                context_parts.append(f"Next: {segments[i+1].get('text', '')}")

            context = " ".join(context_parts)

            correction_result = self.correct_text(text, context, language=language)

            corrected_segment = segment.copy()
            corrected_segment['text'] = correction_result.corrected_text
            corrected_segment['original_text'] = correction_result.original_text
            corrected_segment['correction_confidence'] = correction_result.confidence

            corrected_segments.append(corrected_segment)
            logger.info(f"Corrected segment {i+1}/{len(segments)}: {text[:30]}...")

        return corrected_segments
