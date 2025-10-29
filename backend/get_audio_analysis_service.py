import logging

logger = logging.getLogger("celery")


class GetAudioAnalysisService:
    def process(self):
        try:
            pass

        except Exception as e:
            logger.exception(e)
            return None