import os
import logging
from backend.util.util import Util
from backend.audio.file_content_save import FileContentSave
logger = logging.getLogger("celery")


class TranscriptSave(FileContentSave):

    def save_trasnscript(self, transcript: str, audio_path: str) -> str:

        try:
            folder_path = Util.get_path_from_absolute_path(audio_path)
            file_name = Util.get_file_name_without_extension(audio_path)
            transcript_file_name = f"{file_name}_transcript.txt"
            file_path = os.path.join(folder_path, transcript_file_name)
            result = self.save_content_to_file(transcript, file_path)
            if result:
                return "Transcript saved Successful."
            return "Can not save transcript."

        except Exception as e:
            logger.exception(e)
            return "Error while saving."

    def save_clean_transcript(self, transcript: str, audio_path: str) -> str:

        try:
            folder_path = Util.get_path_from_absolute_path(audio_path)
            file_name = Util.get_file_name_without_extension(audio_path)
            transcript_file_name = f"{file_name}_clean_transcript.txt"
            file_path = os.path.join(folder_path, transcript_file_name)
            result = self.save_content_to_file(transcript, file_path)
            if result:
                return "Clean Transcript saved Successful."
            return "Can not save clean transcript."

        except Exception as e:
            logger.exception(e)
            return "Error while saving clean."
