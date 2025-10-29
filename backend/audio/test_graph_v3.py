from langgraph.graph import StateGraph, END
from typing import TypedDict


# --- Define State ---
class State(TypedDict):
    audio_file: str
    language: str
    transcript: str
    cleaned_transcript: str
    translation: str
    result: dict


# --- Workflow Class ---
class AudioPipeline:
    def __init__(self):
        self.workflow = StateGraph(State)
        self._build_graph()

    # --- Node Functions ---
    def read_audio_file(self, state: State):
        state["audio_file"] = "sample.wav"
        return state

    def select_model(self, state: State):
        lang = state.get("language", "").lower()
        if lang == "english":
            return "english"
        elif lang == "tamil":
            return "tamil"
        else:
            return "default"

    def whisper_for_transcript(self, state: State):
        state["transcript"] = "Whisper transcript"
        return state

    def openai_for_transcript(self, state: State):
        state["transcript"] = "OpenAI transcript"
        return state

    def azure_for_transcript(self, state: State):
        state["transcript"] = "Azure transcript"
        return state

    def save_transcript(self, state: State):
        print("Transcript saved:", state["transcript"])
        return state

    def clean_transcript(self, state: State):
        lang = state.get("language", "").lower()
        if lang == "hindi":
            return "hindi"
        else:
            return "other"

    def openai_4o_mini(self, state: State):
        state["cleaned_transcript"] = "Cleaned with 4o mini"
        return state

    def openai_4o(self, state: State):
        state["cleaned_transcript"] = "Cleaned with 4o"
        return state

    def save_translate(self, state: State):
        state["translation"] = f"Translated: {state['cleaned_transcript']}"
        print("Translation saved:", state["translation"])
        return state

    # --- Build Graph ---
    def _build_graph(self):
        wf = self.workflow

        # Nodes
        wf.add_node("read_audio", self.read_audio_file)
        wf.add_node("whisper", self.whisper_for_transcript)
        wf.add_node("openai", self.openai_for_transcript)
        wf.add_node("azure", self.azure_for_transcript)
        wf.add_node("save_transcript", self.save_transcript)
        wf.add_node("clean_transcript", self.clean_transcript)
        wf.add_node("openai_mini", self.openai_4o_mini)
        wf.add_node("openai_full", self.openai_4o)
        wf.add_node("save_translate", self.save_translate)

        # Entry
        wf.set_entry_point("read_audio")

        # Branch: select model
        wf.add_conditional_edges("read_audio", self.select_model, {
            "english": "whisper",
            "tamil": "openai",
            "default": "azure"
        })

        # Merge back to save_transcript
        wf.add_edge("whisper", "save_transcript")
        wf.add_edge("openai", "save_transcript")
        wf.add_edge("azure", "save_transcript")

        # Branch: clean transcript
        wf.add_conditional_edges("save_transcript", self.clean_transcript, {
            "hindi": "openai_mini",
            "other": "openai_full"
        })

        # Merge back to save_translate → end
        wf.add_edge("openai_mini", "save_translate")
        wf.add_edge("openai_full", "save_translate")
        wf.add_edge("save_translate", END)

        # Compile
        self.app = wf.compile()

    # Run pipeline
    def run(self, input_state: State):
        return self.app.invoke(input_state)


# --- Usage ---
pipeline = AudioPipeline()
final_state = pipeline.run({"language": "english"})
print("Final State:", final_state)

# --- Export Graph ---
dot = pipeline.app.get_graph().draw_mermaid_png()  # OR draw_mermaid_pdf()

with open("workflow_v3.jpeg", "wb") as f:
    f.write(dot)
