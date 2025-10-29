from typing import TypedDict
from langgraph.graph import StateGraph, END


# Define the state of the graph
class AgentState(TypedDict):
    value: int


# Define the nodes
def node_A(state: AgentState) -> AgentState:
    print("Executing Node A")
    return {"value": state["value"] + 1}


def node_B(state: AgentState) -> AgentState:
    print("Executing Node B")
    return {"value": state["value"] * 2}


# Define the routing function for the conditional edge
def decide_next_step(state: AgentState) -> str:
    if state["value"] < 5:
        print(f"Condition met: value is {state['value']}. Routing to node_B.")
        return "node_B"
    else:
        print(f"Condition not met: value is {state['value']}. Ending graph.")
        return END


# Build the graph
builder = StateGraph(AgentState)
builder.add_node("node_A", node_A)
builder.add_node("node_B", node_B)

# Add the conditional edge
builder.add_conditional_edges(
    "node_A",  # Source node of the conditional edge
    decide_next_step,  # The routing function
    {
        "node_B": "node_B",  # If decide_next_step returns "node_B", go to node_B
        END: END,  # If decide_next_step returns END, terminate the graph
    }
)

# Set the entry point
builder.set_entry_point("node_A")

# Compile and run the graph
app = builder.compile()

print("\n--- Running with initial value 2 ---")
result1 = app.invoke({"value": 2})
print(f"Final state: {result1}")

print("\n--- Running with initial value 5 ---")
result2 = app.invoke({"value": 5})
print(f"Final state: {result2}")
