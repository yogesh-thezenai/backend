import os
from celery import shared_task
import logging
from backend.analyze_audio_service import AnalyzeAudioService

logger = logging.getLogger("celery")

@shared_task
def analyze_audio_file(file_id, file_path, language, process_name):
    try:
        print("this is the subtask")
        logger.info("this is the subtask")
        audio_service = AnalyzeAudioService()
        audio_service.process(file_id, file_path, language, process_name)
        logger.info("task is completed")

    except Exception as e:
        logger.exception(e)


