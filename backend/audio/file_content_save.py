import os
import logging
from backend.util.util import Util

logger = logging.getLogger("celery")


class FileContentSave:
    def save_content_to_file(self, content: str, file_path: str) -> bool:

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return True

        except Exception as e:
            logger.exception(e)
            return False
