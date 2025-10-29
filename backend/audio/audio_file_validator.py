import os
import logging
from pydub import AudioSegment

from backend.util.util import Util
logger = logging.getLogger("celery")


class AudioFileValidator:

    def validate_file(self, file_path: str) -> bool:
        """
        This method will check for the valid file that can
        be processed. This method will take care of file extension
        and content type.
        :param file_path: path of the audio file
        :return: True if valid audio file
                False if invalid
        """
        try:
            # Step 1: Check if file exists
            if not os.path.exists(file_path):
                return False

            # Step 2: Check for valid extenstion
            valid_extensions = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in valid_extensions:
                return False

            _ = AudioSegment.from_file(file_path)
            return True

        except Exception as e:
            logger.exception(e)
            return None

