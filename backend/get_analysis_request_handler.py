import os
import logging
from django.conf import settings

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from backend.models.analysis_model import AgentEvaluation

from backend.file_manager.file_handler import FileHandler
from .tasks import analyze_audio_file

logger = logging.getLogger("django")


class GetAnalysisRequestHandler(APIView):
    def post(self, request):
        try:
            file_id = request.data.get('file_id')

            # Validation
            if not file_id:
                return Response(
                    {"error": "file_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            evaluations = AgentEvaluation.objects.filter(file_id=file_id)
            print(evaluations.__dict__)
            if not evaluations.exists():
                return Response({"status": "No evaluation found for this file_id"},
                                status=status.HTTP_404_NOT_FOUND)

            data = []
            for eval in evaluations:
                business_metrics = [
                    {
                        "id": bm.id,
                        "greet_intro": bm.greet_intro,
                        "greet_intro_pg": bm.greet_intro_pg,
                        "greet_intro_agent_intro": bm.greet_intro_agent_intro,
                        "cust_verf": bm.cust_verf,
                        "cust_verf_correct": bm.cust_verf_correct,
                        "cust_verf_acc": bm.cust_verf_acc,
                        "call_purp": bm.call_purp,
                        "call_purp_clear": bm.call_purp_clear,
                        "call_purp_tone": bm.call_purp_tone,
                        "total_score": bm.total_score,
                        "max_score": bm.max_score,
                    }
                    for bm in eval.business_metrics.all()
                ]

                customer_metrics = [
                    {
                        "id": cm.id,
                        "metric_name": cm.metric_name,
                        "score": cm.score,
                        "max_score": cm.max_score,
                        "comment": cm.comment,
                    }
                    for cm in eval.customer_error_metrics.all()
                ]

                data.append({
                    "id": eval.id,
                    "file_id": eval.file_id,
                    "evaluation_type": eval.evaluation_type,
                    "created_at": eval.created_at,
                    "business_metrics": business_metrics,
                    "customer_error_metrics": customer_metrics,
                })

            return Response({"status": "ok", "results": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
