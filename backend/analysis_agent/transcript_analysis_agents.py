import logging
from typing import TypedDict, List
import json
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
# from langchain_openai import ChatOpenAI
from typing import Annotated, List
from langgraph.graph.message import add_messages

from langchain_openai import AzureChatOpenAI
logger = logging.getLogger("celery")


llm = AzureChatOpenAI(
    deployment_name="gpt-5-mini",   # 👈 your Azure deployment name (NOT model name!)
    azure_endpoint="https://yoges-mdbraw1t-eastus2.cognitiveservices.azure.com/",
    api_key="<enter key>",
    api_version="2024-12-01-preview",     # must match API version you enabled
    temperature=1
)


# -----------------------------
# Define the global state
# -----------------------------
class State(TypedDict):
    input_transcript: str
    mini_outputs: Annotated[List[dict], lambda old, new: old + new]
    cleaned_output: dict

class TranscriptAnalysisAgents:

    def __init__(self):
        self.workflow = StateGraph(State)
        self._build_graph()

    # Consolidator
    def consolidate_agent(self, state: State) -> dict:
        minis = state.get("mini_outputs", [])
        consolidated = []
        print("++"*10)
        print(type(minis))

        return {"consolidated_output": minis}

    def _build_graph(self):
        try:
            wf = self.workflow
            wf.add_node("business_critical_agent", self.business_critical_agent)
            wf.add_node("customer_critical_error_agent", self.customer_critical_error_agent)
            wf.add_node("consolidate", self.consolidate_agent)

            # Start edges: run all mini agents in parallel
            wf.add_edge("__start__", "business_critical_agent")
            wf.add_edge("__start__", "customer_critical_error_agent")

            # All mini agents go to consolidation
            wf.add_edge("business_critical_agent", "consolidate")
            wf.add_edge("customer_critical_error_agent", "consolidate")

            # End after consolidation
            wf.add_edge("consolidate", END)

            # Compile the graph
            self.app = wf.compile()


        except Exception as e:
            logger.exception(e)
            raise e

    # ---- Run Pipeline ----
    def run(self, input_state: State):
        return self.app.invoke(input_state)


    def customer_critical_error_agent(self, state: State):
        text = state["input_transcript"]
        description = """
                        You are Call Center Call Analyst. You are getting call transcript.
                        Your job is to take care of below parts and score that part, in bracket total score and json key is there:
                        1. Compliance and Regulatory Adherence (15, comp_reg_adhr)
                            a. Customer Centricity and Professionalism (5, comp_reg_adhr_ccp)
                            b. Politeness and Courtesy (5, comp_reg_adhr_pc)
                            c. Product or Process knowledge so that complete and correct information is shared (5,comp_reg_adhr_ppk) 
                        2. Closing (17, closing)
                            a. Proper closing of the call (4, closing_proper)
                            b. Reiteration of key points eg. payment amount, due date (4, closing_reiterate)
                            c. Right Disposition update (5, closing_disposition)
                            d. Thanking the customer (4, closing_thanking)
                        
                        Return the result in below json format:
                        {comp_reg_adhr: {score: <>, max_score: <>, comment: <>}, 
                         comp_reg_adhr_ccp: {score: <>, max_score: <>, comment: <>.}, 
                         comp_reg_adhr_pc: {score: <>, max_score: <>, comment: <>},
                         comp_reg_adhr_ppk: {score: <>, max_score: <>, comment: <>}, 
                         closing: {score: <>, max_score: <>, comment: <>}, 
                         closing_proper: {score: <>, max_score: <>, comment: <>}, 
                         closing_reiterate: {score: <>, max_score: <>, comment: <>}, 
                         closing_disposition: {score: <>, max_score: <>, comment: <>}, 
                         closing_thanking: {score: <>, max_score: <>, comment: <>}}

                        """
        resp = llm.invoke([{"role": "system", "content": description},
                           {"role": "user", "content": text}])

        # print(resp)
        parsed_content = json.loads(resp.content)
        return {"mini_outputs": [{"customer_critical_error_agent": parsed_content}]}


    def business_critical_agent(self, state: State):
        text = state["input_transcript"]
        description = """
                        You are Call Center Call Analyst. You are getting call transcript.
                        Your job is to take care of below parts and score that part, in bracket total score and json key is there:
                        1. Greeting & Introduction (8, greet_intro)
                            a. Proper Greeting (4, greet_intro_pg)
                            b. Agent introduces themselves and the company (4, greet_intro_agent_intro)
                        2. Customer Verification (10, cust_verf)
                            a. Correct verification process followed (5, cust_verf_correct)
                            b. Customer information accurately verified (5, cust_verf_acc)
                        3. Purpose of Call (8, call_purp)
                            a. Clear and concise explanation of the call's purpose (4, call_purp_clear)
                            b. Appropriate tone and language (4, call_purp_tone)
    
                        Return the result in json format given below.
                        {greet_intro: <>, greet_intro_pg: <>, greet_intro_agent_intro: <>, cust_verf: <>, cust_verf_correct: <>, cust_verf_acc: <>, call_purp: <>, call_purp_clear: <>, call_purp_tone: <>, total_score: <>, max_score: <>}
                        """
        resp = llm.invoke([{"role": "system", "content": description},
                           {"role": "user", "content": text}])

        parsed_content = json.loads(resp.content)
        return {"mini_outputs": [{"business_critical_agent": parsed_content}]}


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
    agents  = TranscriptAnalysisAgents()
    result = agents.run({
        "input_transcript": transcript,
        "mini_outputs": [],
        "cleaned_output": {}
    })
    # result = app.invoke({
    #     "input_prompt": transcript,
    #     "mini_outputs": [],
    #     "consolidated_output": ""
    # })
    print("Mini agent outputs:", result["mini_outputs"])

