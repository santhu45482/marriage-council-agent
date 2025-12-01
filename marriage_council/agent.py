from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, FunctionTool
from .config import conf
from .sub_agents import get_vetting_workflow, groom_rep, bride_rep
from .tools import calculate_utility_score, get_random_profile_id, get_profile_details

# The Root Agent
root_agent = Agent(
    name="marriage_broker_agent",
    model=Gemini(model=conf.model_smart),
    tools=[
        AgentTool(get_vetting_workflow()),
        AgentTool(groom_rep),
        AgentTool(bride_rep),
        FunctionTool(calculate_utility_score),
        FunctionTool(get_random_profile_id),
        FunctionTool(get_profile_details)
    ],
    instruction="""You are the Chief Marriage Broker.
    
    1. **VETTING:** Call .
       - IF "DECISION: FAIL": Output "VERDICT: MATCH REJECTED" and STOP.
       - IF "DECISION: PASS": Output "VERDICT: VETTING PASSED" and continue.
       
    2. **NEGOTIATION:**
       - Consult Reps.
       - Propose Compromise.
       - Verify with .
       - Output "MATCH SUCCESSFUL" if score > 60, else "NEGOTIATION FAILED".
    """
)
