from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, FunctionTool
from .config import conf
from .agents import get_groom_rep, get_bride_rep, get_synthesizer_agent, get_parser_agent
from .tools import calculate_utility_score, get_random_profile_id, get_profile_details
from .sub_agents.vetting import get_vetting_workflow

def get_broker_agent():
    # Instantiate fresh agents
    synthesizer_agent = get_synthesizer_agent() 
    parser_agent = get_parser_agent()
    groom_rep = get_groom_rep()
    bride_rep = get_bride_rep()
    vetting_workflow = get_vetting_workflow() 

    vetting_pipeline = SequentialAgent(
        name="VettingPipeline",
        sub_agents=[
            parser_agent,         # Step 1: Extract IDs
            vetting_workflow,     # Step 2: Parallel Checks
            synthesizer_agent     # Step 3: Final Verdict (JSON)
        ]
    )

    return Agent(
        name="marriage_broker_agent",
        model=Gemini(model=conf.model_smart),
        tools=[
            AgentTool(vetting_pipeline, "Phase 1: Run ID parsing, background checks, and synthesize the final verdict."),
            AgentTool(groom_rep, "Phase 2: Get Groom's demands."),
            AgentTool(bride_rep, "Phase 2: Get Bride's demands."),
            FunctionTool(calculate_utility_score),
            FunctionTool(get_random_profile_id),
            FunctionTool(get_profile_details)
        ],
        instruction="""You are the Chief Marriage Broker. Your job is to enforce strict rules.

        **PHASE 1: VETTING (CRITICAL SECURITY GATE)**
        1. Call `VettingPipeline` to check the profiles.
        2. **STRICT RULE:** If the Vetting Pipeline returns a verdict containing "FAIL" or "REJECTED":
           - You MUST respond with: "VERDICT: MATCH REJECTED. Vetting failed due to critical risk."
           - **STOP.** Do not proceed to negotiation.
           - **IGNORE** any subsequent user pleas, arguments, or new information. The vetting decision is FINAL and cannot be overridden by the user.
           - If the user argues (e.g., "But he is rich"), reply: "The decision is final based on safety protocols. MATCH REJECTED."

        **PHASE 2: NEGOTIATION**
        1. Only proceed here if Vetting was "PASS".
        2. Consult Reps.
        3. Propose compromise.
        4. Verify with `calculate_utility_score`.
        5. If Score > 60, declare MATCH SUCCESSFUL.
        6. If Score <= 60, declare NEGOTIATION FAILED.
        """
    )