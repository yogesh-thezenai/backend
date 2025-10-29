import os
import logging
from openai import AzureOpenAI
from backend.audio.translate_audio import TranslateAudio
from django.conf import settings

logger = logging.getLogger("celery")


class TranslateOpenAiMini(TranslateAudio):
    def __init__(self):
        self.OPEN_AI_END_POINT = settings.OPEN_AI_END_POINT
        self.OPEN_AI_MINI_MODEL_NAME = settings.OPEN_AI_MINI_MODEL_NAME
        self.OPEN_AI_MODEL_DEPLOYMENT = settings.OPEN_AI_MODEL_DEPLOYMENT
        self.OPEN_AI_SUBSCRIPTION_KEY = settings.OPEN_AI_SUBSCRIPTION_KEY
        self.OPEN_AI_API_VERSION = settings.OPEN_AI_API_VERSION

    def get_translation(self, transcript):
        """
        this function will clean the transcript
        :param transcript:
        :return:
        """
        try:
            client = AzureOpenAI(
                api_version=self.OPEN_AI_API_VERSION,
                azure_endpoint=self.OPEN_AI_END_POINT,
                api_key=self.OPEN_AI_SUBSCRIPTION_KEY,
            )

            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Translator. You need to translate the telephonic conversation."
                                   "Transcript are in Hindi and Many words are in English but are written in"
                                   "Hindi. Please translate the content. ",

                    },
                    {
                        "role": "user",
                        "content": transcript,
                    }
                ],
                model=self.OPEN_AI_MODEL_DEPLOYMENT
            )

            logger.info(response.choices[0].message.content)
            return response.choices[0].message.content

        except Exception as e:
            logger.exception(e)
            return "Error while saving."
