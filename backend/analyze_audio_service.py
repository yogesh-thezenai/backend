import logging
from backend.audio.audio_pipeline import AudioPipeline
from backend.analysis_agent.transcript_analysis_agents import TranscriptAnalysisAgents
from backend.models.analysis_model import AgentEvaluation, BusinessCriticalMetric, CustomerCriticalErrorMetric

logger = logging.getLogger("celery")


class AnalyzeAudioService:
    def process(self, file_id, file_path, language, process_name):
        try:
            logger.info(f" file id: {file_id} file_path: {file_path}, language: {language}, process_name: {process_name}")
            print(f"file id: {file_id} ,file_path: {file_path}, language: {language}, process_name: {process_name}")
            pipeline = AudioPipeline()
            transcript_details = pipeline.run({"language": language, "audio_file": file_path})
            print("===========================================================================================")
            print(transcript_details)
            print(type(transcript_details))
            print(transcript_details["cleaned_transcript"])
            # saving the result

            # use the result for call classification

            # use the agents for call analysis
            agents = TranscriptAnalysisAgents()
            transcript_analysis = agents.run({
                "input_transcript": str(transcript_details["cleaned_transcript"]),
                "mini_outputs": [],
                "cleaned_output": {}
            })

            print("++"*20)
            print(transcript_analysis)
            print(type(transcript_analysis))
            result = transcript_analysis["mini_outputs"]
            print("++saving result++" * 20)
            print(type(result))
            print(result)
            # save business_critical_agent
            biz_eval = AgentEvaluation.objects.create(file_id=file_id, evaluation_type="business_critical_agent")
            BusinessCriticalMetric.objects.create(evaluation=biz_eval, **result[0]["business_critical_agent"])

            print(f"saved business critical details{result[0]}")

            # save customer_critical_error_agent
            cust_eval = AgentEvaluation.objects.create(file_id=file_id, evaluation_type="customer_critical_error_agent")
            for name, details in result[1]["customer_critical_error_agent"].items():
                print(name)
                print(details)
                details.update({"metric_name": name})
                print(details)
                CustomerCriticalErrorMetric.objects.create(
                    evaluation=cust_eval,**details)

            print("saved customer critical error agent")


        except Exception as e:
            logger.exception(e)
            print(e)