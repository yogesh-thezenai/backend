import os
import logging
from backend.util.util import Util
from backend.audio.file_content_save import FileContentSave
logger = logging.getLogger("celery")


class TranslateSave(FileContentSave):

    def save_translation(self, translation: str, audio_path: str) -> str:

        try:
            folder_path = Util.get_path_from_absolute_path(audio_path)
            file_name = Util.get_file_name_without_extension(audio_path)
            transcript_file_name = f"{file_name}_translate.txt"
            file_path = os.path.join(folder_path, transcript_file_name)
            result = self.save_content_to_file(translation, file_path)
            if result:
                return file_path
            return "Can not save transcript."

        except Exception as e:
            logger.exception(e)
            return "Error while saving."
