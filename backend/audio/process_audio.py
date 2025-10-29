
import logging

logger = logging.getLogger("celery")


class ProcessAudio:

    def get_transcript_model(self, lang, file_path):
        """
        This function will find the best model for the audio
        :return: model name
                 default model name is azure
        """
        try:
            if lang == "english":
                return "whisper"
            elif lang == "tamil":
                return "openai"

            else:
                return "azure"

        except Exception as e:
            logger.exception(e)
            return "azure"



