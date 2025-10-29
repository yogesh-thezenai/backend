from typing import TypedDict, List
from langgraph.graph import StateGraph
from typing import Annotated
import operator
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
# ------------------------------------------------------------
# Step 1. Define the state
# ------------------------------------------------------------
class State(TypedDict):
    input_text: str
    # allow multiple updates -> appends results
    mini_outputs: Annotated[list, operator.add]
    consolidated_output: str


# ------------------------------------------------------------
# Step 2. Define your agents
# ------------------------------------------------------------

# "OpenAI agent" (could call an LLM)
def openai_agent(state: State) -> dict:
    text = state["input_text"]
    return {"input_text": f"OpenAI processed: {text}"}

# Mini agents
def mini_agent_1(state: State) -> dict:
    return {"mini_outputs": state.get("mini_outputs", []) + ["mini1 says hi"]}

def mini_agent_2(state: State) -> dict:
    return {"mini_outputs": state.get("mini_outputs", []) + ["mini2 processed"]}

def mini_agent_n(state: State) -> dict:
    return {"mini_outputs": state.get("mini_outputs", []) + ["miniN finished"]}

# Consolidator
def consolidate_agent(state: State) -> dict:
    minis = state.get("mini_outputs", [])
    consolidated = " | ".join(minis)
    return {"consolidated_output": f"Consolidated: {consolidated}"}


# ------------------------------------------------------------
# Step 3. Build LangGraph
# ------------------------------------------------------------
wf = StateGraph(State)

# Add nodes
wf.add_node("openai_agent", openai_agent)
wf.add_node("mini_agent_1", mini_agent_1)
wf.add_node("mini_agent_2", mini_agent_2)
wf.add_node("mini_agent_n", mini_agent_n)
wf.add_node("consolidate_agent", consolidate_agent)

# Entry point → first goes through OpenAI agent
wf.set_entry_point("openai_agent")

# Then branch into mini agents
wf.add_edge("openai_agent", "mini_agent_1")
wf.add_edge("openai_agent", "mini_agent_2")
wf.add_edge("openai_agent", "mini_agent_n")

# Finally consolidate
wf.add_edge("mini_agent_1", "consolidate_agent")
wf.add_edge("mini_agent_2", "consolidate_agent")
wf.add_edge("mini_agent_n", "consolidate_agent")

# Set finishing node
wf.set_finish_point("consolidate_agent")

# Compile
app = wf.compile()

# ------------------------------------------------------------
# Step 4. Run it
# ------------------------------------------------------------
if __name__ == "__main__":
    result = app.invoke({"input_text": "test input", "mini_outputs": [], "consolidated_output": ""})
    print(result)
