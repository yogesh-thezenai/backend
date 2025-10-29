from langgraph.graph import StateGraph, END
from typing import TypedDict


# Define state
class State(TypedDict):
    audio_file: str
    language: str
    transcript: str
    cleaned_transcript: str
    translation: str


# --- Nodes (functions) ---
def start(state: State):
    print("Start pipeline")
    return state


def read_audio_file(state: State):
    # Stub for reading audio
    state["audio_file"] = "sample_audio.wav"
    return state


def select_model(state: State):
    lang = state.get("language", "default").lower()
    if lang == "english":
        return "whisper"
    elif lang == "tamil":
        return "openai"
    else:
        return "azure"


def whisper_for_transcript(state: State):
    state["transcript"] = "Transcribed with Whisper"
    return state


def openai_for_transcript(state: State):
    state["transcript"] = "Transcribed with OpenAI"
    return state


def azure_for_transcript(state: State):
    state["transcript"] = "Transcribed with Azure"
    return state


def save_transcript(state: State):
    print("Transcript saved:", state["transcript"])
    return state


def clean_transcript(state: State):
    # Decision: choose model for cleaning
    if len(state["transcript"]) < 50:  # simple condition
        return "openai_mini"
    else:
        return "openai_full"


def openai_4o_mini(state: State):
    state["cleaned_transcript"] = "Cleaned with OpenAI 4o mini"
    return state


def openai_4o(state: State):
    state["cleaned_transcript"] = "Cleaned with OpenAI 4o"
    return state


def save_translate(state: State):
    state["translation"] = f"Translated: {state['cleaned_transcript']}"
    print("Translation saved:", state["translation"])
    return state


# --- Build Graph ---
# --- Build Graph ---
workflow = StateGraph(State)

workflow.add_node("read_audio", read_audio_file)
workflow.add_node("whisper", whisper_for_transcript)
workflow.add_node("openai", openai_for_transcript)
workflow.add_node("azure", azure_for_transcript)
workflow.add_node("save_transcript", save_transcript)
workflow.add_node("clean_transcript", clean_transcript)
workflow.add_node("openai_mini", openai_4o_mini)
workflow.add_node("openai_full", openai_4o)
workflow.add_node("save_translate", save_translate)

# Entry point
workflow.set_entry_point("read_audio")

# Edges
workflow.add_conditional_edges("read_audio", select_model, {
    "whisper": "whisper",
    "openai": "openai",
    "azure": "azure"
})
workflow.add_edge("whisper", "save_transcript")
workflow.add_edge("openai", "save_transcript")
workflow.add_edge("azure", "save_transcript")
workflow.add_conditional_edges("save_transcript", clean_transcript, {
    "openai_mini": "openai_mini",
    "openai_full": "openai_full"
})
workflow.add_edge("openai_mini", "save_translate")
workflow.add_edge("openai_full", "save_translate")
workflow.add_edge("save_translate", END)

# Compile
app = workflow.compile()

# Run example
final_state = app.invoke({"language": "english"})
print("Final state:", final_state)

final_state = app.invoke({"language": "hindi"})
print("Final state:", final_state)
