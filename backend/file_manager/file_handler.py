import os
import logging
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.conf import settings
from backend.util.util import Util
logger = logging.getLogger("django")
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class FileHandler:

    def save_audio_file(self, uploaded_file: str) -> str:
        """
        This function will create a unique folder in the MEDIA_ROOT
        Then save the file inside that.
        :param uploaded_file:
        :return:
        """
        try:
            folder_name = Util.create_unique_folder_name(file_name=uploaded_file.name)
            # Define storage inside MEDIA_ROOT/audio_files/<unique_folder>/
            folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            logger.info(folder_path)
            # File save path
            file_path = os.path.join(folder_path, uploaded_file.name)

            # Save file in chunks
            with open(file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Relative path (to store in DB or return in response)
            file_relative_path = file_path

            return file_relative_path

        except Exception as e:
            logger.exception(e)
            return None

