from abc import ABC, abstractmethod


class TranscriptBase:
    LANGUAGE_MAP = {
        "english": "en-US",
        "hindi": "hi-IN",
        "french": "fr-FR",
        "spanish": "es-ES",
        "german": "de-DE",
        "italian": "it-IT",
        "japanese": "ja-JP",
        "chinese": "zh-CN"
    }

    def __init__(self, language: str = "english"):
        """
        Base class for transcription services.
        :param language: Human-readable language name (default: english)
        """

        self.language = self._get_language_code(language)
        print("===printing language"*20)
        print(self.language)

    def _get_language_code(self, language: str) -> str:
        """Convert human-readable language to Azure-compatible code."""
        print(language)
        lang =  self.LANGUAGE_MAP.get(language.lower(), self.LANGUAGE_MAP["english"])
        print("==="*10)
        print(lang)
        return lang

    @abstractmethod
    def transcribe_audio(self, audio_file: str, sample_rate: int) -> str:
        """
        Abstract method to transcribe audio files.
        Must be implemented by subclasses.
        :param sample_rate: file sampling rate
        :param audio_file: Path to audio file
        :return: Transcript text
        """
        pass

