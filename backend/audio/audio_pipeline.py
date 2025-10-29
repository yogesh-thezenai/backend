import logging
from langgraph.graph import StateGraph, END
from typing import TypedDict

from backend.audio.audio_file_validator import AudioFileValidator
from backend.audio.process_audio import ProcessAudio
from backend.audio.transcript_azure import TranscriptAzure
from backend.audio.transcript_save import TranscriptSave
from backend.audio.translate_save import TranslateSave
from backend.audio.transcript_clean_openai5 import TranscriptCleanOpenAi5
from backend.audio.translate_openai_mini import TranslateOpenAiMini

logger = logging.getLogger("celery")


# --- Define State ---
class State(TypedDict):
    audio_file: str
    is_valid_file: bool
    language: str
    transcript: str
    cleaned_transcript: str
    translation: str
    result: dict


# --- Workflow class ---
class AudioPipeline:
    def __init__(self):
        self.workflow = StateGraph(State)
        self._build_graph()

    # ---- Node functions ----
    def validate_audio_file(self, state: State):
        try:
            validator = AudioFileValidator()
            is_valid = validator.validate_file(state["audio_file"])
            state["is_valid_file"] = is_valid
            # state["is_valid_file"] = True
        except Exception as e:
            logger.exception(e)

        return state

    def select_model(self, state: State):
        """
        this node will select the model for transcript
        on the basis of language for now
        :param state:
        :return:
        """
        try:
            if state["is_valid_file"]:
                lang = state["language"]
                process_audio = ProcessAudio()
                logger.info(lang)
                logger.info(state["audio_file"])
                model_name = process_audio.get_transcript_model(lang, state["audio_file"])
                logger.info(f"model_name:{model_name}")
                return model_name
            logger.info("returning the default as file is not valid")
            return "azure"
        except Exception as e:
            logger.exception(e)
            return "azure"

    def whisper_for_transcript(self, state: State):
        state["transcript"] = "Transcribed with Whisper"
        return state

    def openai_for_transcript(self, state: State):
        state["transcript"] = "Transcribed with OpenAI"
        return state

    def azure_for_transcript(self, state: State):
        try:
            logger.info("inside azure transcript")
            language = state.get("language", "hindi").lower()
            logger.info(language)
            file_path = state["audio_file"]
            az_transcript = TranscriptAzure(language)
            sample_rate = 16000
            transcript = az_transcript.transcribe_audio(file_path, sample_rate)
            logger.info(transcript)
            state["transcript"] = transcript
            return state
        except Exception as e:
            logger.exception(e)
            state["transcript"] = "Error in transcription"
            return state

    def save_transcript(self, state: State):
        try:
            ts = TranscriptSave()
            result = ts.save_trasnscript(state["transcript"], state["audio_file"])
            logger.info(result)
            cln_trans_openai = TranscriptCleanOpenAi5()
            logger.info(state["transcript"])
            cln_trans = cln_trans_openai.get_clean_transcript(state["transcript"])
            state["cleaned_transcript"] = cln_trans
            result = ts.save_clean_transcript(state["cleaned_transcript"], state["audio_file"])
            return state
        except Exception as e:
            logger.exception(e)
            return state

    def clean_transcript(self, state: State):
        try:
            # state["cleaned_transcript"] = state["transcript"]
            if state["language"] == "english":
                return "openai_mini"
            if state["language"] == "tamil":
                return "openai_full"
            else:
                return "openai_mini"
        except Exception as e:
            logger.exception(e)
        return "openai_mini"

    def openai_4o_mini(self, state: State):
        try:
            logger.info("going for translation mini")
            logger.info(f"Pipeline state keys: {list(state.keys())}")
            trans_openai = TranslateOpenAiMini()
            cln_transc = state["cleaned_transcript"]
            logger.info(cln_transc)
            cln_trans = trans_openai.get_translation(cln_transc)
            state["translation"] = cln_trans
        except Exception as e:
            logger.exception(e)
            state["translation"] = state["cleaned_transcript"]
        return state

    def openai_4o(self, state: State):
        try:
            logger.info("going for translation openai 4o")
            trans_openai = TranslateOpenAiMini()
            cln_trans = trans_openai.get_translation(state["cleaned_transcript"])
            state["translation"] = cln_trans
        except Exception as e:
            logger.exception(e)
            state["translation"] = state["cleaned_transcript"]
        return state

    def save_translate(self, state: State):
        try:
            ts = TranslateSave()
            logger.info(state["translation"])
            result = ts.save_translation(state["translation"], state["audio_file"])
            logger.info(result)
            return state
        except Exception as e:
            logger.exception(e)
            return state

    # ---- Build Graph ----
    def _build_graph(self):
        wf = self.workflow
        wf.add_node("validate_audio", self.validate_audio_file)
        wf.add_node("whisper", self.whisper_for_transcript)
        wf.add_node("openai", self.openai_for_transcript)
        wf.add_node("azure", self.azure_for_transcript)
        wf.add_node("save_transcript", self.save_transcript)
        wf.add_node("clean_transcript", self.clean_transcript)
        wf.add_node("openai_mini", self.openai_4o_mini)
        wf.add_node("openai_full", self.openai_4o)
        wf.add_node("save_translate", self.save_translate)

        # Entry point
        wf.set_entry_point("validate_audio")

        # Edges
        wf.add_conditional_edges("validate_audio", self.select_model, {
            "whisper": "whisper",
            "openai": "openai",
            "azure": "azure"
        })
        wf.add_edge("whisper", "save_transcript")
        wf.add_edge("openai", "save_transcript")
        wf.add_edge("azure", "save_transcript")

        wf.add_conditional_edges("save_transcript", self.clean_transcript, {
            "openai_mini": "openai_mini",
            "openai_full": "openai_full"
        })
        wf.add_edge("openai_mini", "save_translate")
        wf.add_edge("openai_full", "save_translate")
        wf.add_edge("save_translate", END)

        # Compile
        self.app = wf.compile()

    # ---- Run Pipeline ----
    def run(self, input_state: State):
        return self.app.invoke(input_state)
