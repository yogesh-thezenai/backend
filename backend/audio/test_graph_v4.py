import logging
from langgraph.graph import StateGraph, END
from typing import TypedDict

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
            state["is_valid_file"] = True
        except Exception as e:
            logger.exception(e)

        return state

    def select_model(self, state: State):
        lang = state.get("language", "default").lower()
        if lang == "english":
            return "whisper"
        elif lang == "tamil":
            return "openai"
        else:
            return "azure"

    def whisper_for_transcript(self, state: State):
        state["transcript"] = "Transcribed with Whisper"
        return state

    def openai_for_transcript(self, state: State):
        state["transcript"] = "Transcribed with OpenAI"
        return state

    def azure_for_transcript(self, state: State):
        state["transcript"] = "Transcribed with Azure"
        return state

    def save_transcript(self, state: State):
        print("Transcript saved:", state["transcript"])
        return state

    def clean_transcript(self, state: State):
        if len(state["transcript"]) < 50:
            return "openai_mini"
        else:
            return "openai_full"

    def openai_4o_mini(self, state: State):
        state["cleaned_transcript"] = "Cleaned with OpenAI 4o mini"
        return state

    def openai_4o(self, state: State):
        state["cleaned_transcript"] = "Cleaned with OpenAI 4o"
        return state

    def save_translate(self, state: State):
        state["translation"] = f"Translated: {state['cleaned_transcript']}"
        print("Translation saved:", state["translation"])
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
        wf.add_conditional_edges("validate_audio_file", self.select_model, {
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


# --- Usage ---
pipeline = AudioPipeline()
final_state = pipeline.run({"language": "english"})
print("Final State:", final_state)

# --- Export Graph ---
dot = pipeline.app.get_graph().draw_mermaid_png()  # OR draw_mermaid_pdf()

with open("workflow_v4.jpeg", "wb") as f:
    f.write(dot)
