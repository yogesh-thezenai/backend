import os
import logging
from openai import AzureOpenAI
from backend.audio.transcript_clean_base import TranscriptCleanBase
from django.conf import settings


logger = logging.getLogger("celery")


class TranscriptCleanOpenAi5(TranscriptCleanBase):

    def __init__(self):
        self.OPEN_AI_END_POINT = settings.OPEN_AI_END_POINT
        self.OPEN_AI_MINI_MODEL_NAME = settings.OPEN_AI_MINI_MODEL_NAME
        self.OPEN_AI_MODEL_DEPLOYMENT = settings.OPEN_AI_MODEL_DEPLOYMENT
        self.OPEN_AI_SUBSCRIPTION_KEY = settings.OPEN_AI_SUBSCRIPTION_KEY
        self.OPEN_AI_API_VERSION = settings.OPEN_AI_API_VERSION

    def get_clean_transcript(self, transcript):
        """
        this function will clean the transcript
        :param transcript:
        :return:
        """
        try:
            logger.info(transcript)
            endpoint = "https://yoges-mdbraw1t-eastus2.cognitiveservices.azure.com/"
            model_name = "gpt-5-mini"
            deployment = "gpt-5-mini"

            subscription_key = "<enter key>"
            api_version = "2024-12-01-preview"

            # client = AzureOpenAI(
            #     api_version=api_version,
            #     azure_endpoint=endpoint,
            #     api_key=subscription_key,
            # )
            logger.info(self.OPEN_AI_API_VERSION)
            logger.info(self.OPEN_AI_END_POINT)
            logger.info(self.OPEN_AI_SUBSCRIPTION_KEY)
            client = AzureOpenAI(
                api_version=self.OPEN_AI_API_VERSION,
                azure_endpoint=self.OPEN_AI_END_POINT,
                api_key=self.OPEN_AI_SUBSCRIPTION_KEY,
            )

            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Transcript analyzer. You need to understand the transcript "
                                   "and correct the out of context words. "
                                   "Please understand the context before changing the word."
                                   "Only correct out-of-context/misheard words (leave wording, grammar, fillers as-is).",
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



