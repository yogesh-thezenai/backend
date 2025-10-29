import os
import logging
import datetime

logger = logging.getLogger("django")


class Util:

    @staticmethod
    def create_unique_folder_name(file_name: str) -> str:
        """
        This method will create a unique name
        it will be in the format file_name_dd_mm_yyyy_hh_mm_ss
        :param file_name:
        :return: file_name string
        """
        try:
            # Get current datetime
            now = datetime.datetime.now()
            timestamp = now.strftime("%d_%m_%Y_%H_%M_%S")

            # Clean up file_name (remove spaces or invalid chars if needed)
            # safe_file_name = file_name.strip().replace(" ", "_")
            safe_file_name = Util.get_file_name_without_extension(file_name)

            # Create final unique name
            unique_name = f"{safe_file_name}_{timestamp}"

            return unique_name

        except Exception as e:
            logger.exception(e)
            return None

    @staticmethod
    def get_file_name_without_extension(file_name: str) -> str:
        """
        this method will get the file name without extension
        :param file_name:
        :return:
        """
        try:
            # os.path.splitext returns a tuple (root, ext)
            name, _ = os.path.splitext(file_name)
            return name

        except Exception as e:
            logger.exception(e)
            return None

    @staticmethod
    def get_file_extension(file_name : str) -> str:
        """
        This method will extract file extension from file name
        :param file_name: str
        :return: str
        """
        try:
            ext = os.path.splitext(file_name)[1].lower()
            return ext
        except Exception as e:
            logger.exception(e)
            return None

    @staticmethod
    def get_path_from_absolute_path(file_path: str) -> str:
        """
        this function will extract the complete folder location from
        a file path
        :param file_path:
        :return: file path
        """
        try:
            if not file_path:
                raise ValueError("file_path cannot be empty")

            folder_path = os.path.dirname(file_path)
            return folder_path
        except Exception as e:
            logger.exception(e)
            return None


if __name__ == "__main__":
    util = Util
    result = util.get_file_extension("/home/yogesh/test document.pdf")
    print(result)
