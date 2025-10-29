import os
import logging
import requests
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from backend.audio.transcript_base import TranscriptBase
from django.conf import settings

logger = logging.getLogger("celery")


class TranscriptAzure(TranscriptBase):
    def __init__(self, language: str = "english"):
        print(f"creating object:{language}")
        super().__init__(language)
        self.subscription_key = settings.AZURE_SUBSCRIPTION_KEY
        self.region = settings.AZURE_REGION
        self.endpoint = (
            f"https://{self.region}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-11-15"
        )
        print("===printing language" * 20)
        print(self.language)


    def transcribe_audio(self, audio_file: str, sample_rate: int) -> str:

        try:
            print("===printing language" * 20)
            print(self.language)
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }

            files = {
                "audio": open(audio_file, "rb"),
                "definition": (None, f'{{"locales":["{self.language}"]}}', "application/json")
            }
            response = requests.post(
                self.endpoint,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            if response.status_code == 200:
                logger.info(response.json())
                result = response.json()
                trans_list = result["combinedPhrases"][0]
                trans_cont = trans_list["text"]
                logger.info(trans_list)
                result = trans_cont
                logger.info(result)

                return result
            return ""

        except Exception as e:
            logger.exception(e)
            return ""
