import os
import logging
import requests
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment

logger = logging.getLogger("celery")


class TranscriptAzure:
    def __init__(self, language: str = "english"):
        # super().__init__(language)
        self.language = "hi-IN"
        self.subscription_key = "2vmiQacLtF35eltzROIOOZ6P37AQNz07tWqDawwRa5qhQY25z8iwJQQJ99BGACHYHv6XJ3w3AAAAACOGylfG"
        self.region = "eastus2"
        self.endpoint = (
            f"https://yoges-mdbraw1t-eastus2.cognitiveservices.azure.com/speechtotext/transcriptions:transcribe?api-version=2024-11-15"
        )


    def transcribe_audio(self, audio_file: str, sample_rate: int) -> str:

        try:
            logger.info(self.language)
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

if __name__ == "__main__":
    file_path = "C:\\Users\\DELL\\workspace\\Projects\\audio_analysis\\workspace_file\\9097763009.wav"
    tz = TranscriptAzure()
    result = tz.transcribe_audio(file_path, 16000)
    print(result)