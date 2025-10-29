from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
# from langchain_openai import ChatOpenAI
from typing import Annotated, List
from langgraph.graph.message import add_messages

from langchain_openai import AzureChatOpenAI


llm = AzureChatOpenAI(
    deployment_name="gpt-5-mini",   # 👈 your Azure deployment name (NOT model name!)
    azure_endpoint="https://yoges-mdbraw1t-eastus2.cognitiveservices.azure.com/",
    api_key="<enter key>",
    api_version="2024-12-01-preview"     # must match API version you enabled
)

# -----------------------------
# Define the global state
# -----------------------------
class State(TypedDict):
    input_prompt: str
    mini_outputs: Annotated[List[dict], lambda old, new: old + new]
    consolidated_output: str


# -----------------------------
# Define mini agents
# -----------------------------
# def business_critical_agent(state: State):
#     text = state["input_prompt"]
#     description = f"""
#                     You are Call Center Call Analyst. You are getting call transcript.
#                     Your job is to take care of below parts and score that part, out of total score written in bracket:
#                     1. Greeting & Introduction (8)
#                         a. Proper Greeting (4)
#                         b. Agent introduces themselves and the company (4)
#                     2. Customer Verification (10)
#                         a. Correct verification process followed (5)
#                         b. Customer information accurately verified (5)
#                     3. Purpose of Call (8)
#                         a. Clear and concise explanation of the call's purpose (4)
#                         b. Appropriate tone and language (4)
#
#                     Return the result in json format.
#                     Below is the transcript:
#                     {text}
#                     """
#     resp = llm.invoke(description)
#     print(resp)
#
#     return {"mini_outputs": [{"business_critical_agent": [str(resp)]}]}

def business_critical_agent(state: State):
    text = state["input_prompt"]
    description = f"""
                    You are Call Center Call Analyst. You are getting call transcript.
                    Your job is to take care of below parts and score that part, out of total score written in bracket:
                    1. Greeting & Introduction (8)
                        a. Proper Greeting (4)
                        b. Agent introduces themselves and the company (4)
                    2. Customer Verification (10)
                        a. Correct verification process followed (5)
                        b. Customer information accurately verified (5)
                    3. Purpose of Call (8)
                        a. Clear and concise explanation of the call's purpose (4)
                        b. Appropriate tone and language (4)

                    Return the result in json format.
                    
                    """
    resp = llm.invoke([{"role": "system", "content": description},
                       {"role": "user", "content": text}])
    print(resp)

    return {"mini_outputs": [{"business_critical_agent": [str(resp)]}]}


def agent_greeting(state: State):
    text = state["input_prompt"]
    if any(word in text.lower() for word in ["hello", "hi", "hey"]):
        return {"mini_outputs": ["Greeting detected ✅"]}
    return {"mini_outputs": ["No greeting found ❌"]}


def agent_sentiment(state: State):
    text = state["input_prompt"]
    if any(word in text.lower() for word in ["good", "happy", "great"]):
        return {"mini_outputs": ["Positive sentiment 🙂"]}
    elif any(word in text.lower() for word in ["bad", "sad", "angry"]):
        return {"mini_outputs": ["Negative sentiment 🙁"]}
    return {"mini_outputs": ["Neutral sentiment 😐"]}


def agent_topic(state: State):
    text = state["input_prompt"]
    if "weather" in text.lower():
        return {"mini_outputs": ["Topic: Weather ☀️"]}
    elif "music" in text.lower():
        return {"mini_outputs": ["Topic: Music 🎵"]}
    return {"mini_outputs": ["Topic: General 💬"]}


# -----------------------------
# Consolidation using OpenAI
# -----------------------------
# llm = ChatOpenAI(model="gpt-4o-mini")


def consolidate_agent(state: State):
    mini_outputs = ""
    mini_results = state["mini_outputs"]
    for key in mini_results:
        print(key)
        # mini_outputs += key
    text = f"""
    The following analysis outputs were received:
    {mini_outputs}

    Please provide a clear consolidated summary.
    """
    # resp = llm.invoke(text)
    # return {"consolidated_output": resp.content}
    return {"consolidated_output": text}


# -----------------------------
# Build the workflow
# -----------------------------
wf = StateGraph(State)

# Add nodes
wf.add_node("business_critical_agent", business_critical_agent)
wf.add_node("agent_greeting", agent_greeting)
wf.add_node("agent_sentiment", agent_sentiment)
wf.add_node("agent_topic", agent_topic)
wf.add_node("consolidate", consolidate_agent)

# Start edges: run all mini agents in parallel
wf.add_edge("__start__", "business_critical_agent")
wf.add_edge("__start__", "agent_greeting")
wf.add_edge("__start__", "agent_sentiment")
wf.add_edge("__start__", "agent_topic")

# All mini agents go to consolidation
wf.add_edge("business_critical_agent", "consolidate")
wf.add_edge("agent_greeting", "consolidate")
wf.add_edge("agent_sentiment", "consolidate")
wf.add_edge("agent_topic", "consolidate")

# End after consolidation
wf.add_edge("consolidate", END)

# Compile the graph
app = wf.compile()

# -----------------------------
# Run Example
# -----------------------------
if __name__ == "__main__":
    transcript = """
    Hello? Hello?
Husband: This is Indira Devi’s husband speaking.
Agent: Sir, this is Maheshwari from Pragati Sangh. Madam had taken a loan with Pragati Sangh.
Husband: Yes.
Agent: Madam used to pay on the 3rd — around 1,920–2,025 rupees on the 3rd, right?
Husband: Yes.
Agent: Now why from the 12th? What’s the problem? It’s been nine months now, hasn’t it?
Husband: Not nine months — because when was our last payment made?
Agent: Your last payment shows as November — it’s recorded as paid on 1st November 2024. Since November your account has been pending.
Husband: At that time her health was very serious; I had admitted her to hospital. After that, when will the installments be paid, madam? What should I do so we can directly transfer the money to you now?
Agent: Can you pay it now?
Husband: Not right now. I’ll be able to go within a week.
Agent: Can you give a date?
Husband: Around the 10th.
Agent: Okay, on the 10th — please try to clear the premium by the 10th.
Husband: We’ll see. We’ll try to pay as much as possible, one, two, three... How do you take payment — online? QR code or cash?
Agent: If there’s a QR code that’s better, because I’m a bit suspicious from the side — since you’re saying the last payment was in November. Earlier I gave money to a client and then their health got worse, so I’m cautious.
Husband: Okay, okay.
Agent: We have two options online. Do you have the loan card, madam?
Husband: Yes, madam, we have the loan card.
Agent: The QR code is on the back of the loan card — you can pay through that. The other option is the Pragati payment link.
Husband: I don’t know about that link.
Agent: You’ll get the link when you go to pay the installment on the 10th. If you say you want to pay by link, I’ll send it to you on the 10th.
Husband: Okay madam, then do it on the 10th — send the link; we’ll pay via the link.
Agent: Either via the link or by scanning the QR — whatever works. Send it to me. You usually pay via link, right? I’ll send it; otherwise it will get sent automatically. Yes, I’ll send you the link.
Husband: I’ll also call you. Please make sure you receive my call because the call will come from this number.
Agent: Okay, I’ll check the number. How much will you clear now — can you tell me the amount?
Husband: I can’t say exactly right now. I’ve just returned to work; I’ll get paid in about four or five days and the rest of the money will come on the 10th. As soon as we get the money, we’ll deposit payment accordingly.
Agent: Fine. I’ll call you again on the 10th. Before I send the link, you have this phone number, right? (Husband confirms ends with three nine.) I’ll call once before sending the link. Tell me how much you’ll pay so I can mention it, then I’ll send the link and you can make the payment through it. If you have any doubt I’ll help you on the call. I can stay on the call while you pay.
Husband: Okay.
Agent: I’ll send you the mail/link on the 10th.
Husband: Okay.
Agent: Also, about your outstanding amount — your final total outstanding is 665.
Husband: Yes, yes, is that final?
Agent: Yes, that’s the full final amount. One minute — as of November, yes. Your loan will close in September this year. You have completed 11 installments in total; one installment (the 12th) is remaining.
Husband: Okay.
Agent: I’ll send you the link and call you on the 10th on this number. Please pick up. If you have any doubts I’ll clear them. Tell me on the 10th how much amount you will have.
Husband: Okay, fine. Thank you for your precious time. Have a good day.
Agent: Okay, okay, sir. Goodbye.
    """
    result = app.invoke({
        "input_prompt": transcript,
        "mini_outputs": [],
        "consolidated_output": ""
    })
    print("Mini agent outputs:", result["mini_outputs"])
    print("Consolidated output:", result["consolidated_output"])

    # --- Export Graph ---
    # dot = app.get_graph().draw_mermaid_png()  # OR draw_mermaid_pdf()
    from langchain_core.runnables.graph_mermaid import MermaidDrawMethod

