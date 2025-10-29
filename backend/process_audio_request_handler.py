import os
import logging
from django.conf import settings

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from backend.models.audio_file import AudioFile

from backend.file_manager.file_handler import FileHandler
from .tasks import analyze_audio_file

logger = logging.getLogger("django")


class FileUploadView(APIView):
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('file')
            language = request.data.get('language')
            process_name = request.data.get('process_name')

            # Validation
            if not uploaded_file or not language or not process_name:
                return Response(
                    {"error": "file, language, and process_name are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Save file in media/uploads/
            fs = FileHandler()
            file_relative_path = fs.save_audio_file(uploaded_file)
            logger.info(file_relative_path)

            full_file_url = request.build_absolute_uri(
                f"{settings.MEDIA_URL}{file_relative_path}"
            )

            # Save record in DB
            record = AudioFile.objects.create(
                file_path=file_relative_path,
                language=language,
                process_name=process_name,
                file_url=full_file_url
            )

            # Trigger background upload
            print(f"before starting the task")
            print(language)
            analyze_audio_file.delay(record.id, file_relative_path, language, process_name)

            return Response({
                "message": "File uploaded and saved successfully",
                "id": record.id,
                "language": record.language,
                "process_name": record.process_name,
                "download_url": record.file_url
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception(e)
            return Response({
                "message": "Error while uploading file.",
                "id": -1,
                "language": "NA",
                "process_name": "NA"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
