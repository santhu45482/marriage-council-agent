from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, FunctionTool
from .config import conf
from .agents import get_groom_rep, get_bride_rep, get_synthesizer_agent, get_parser_agent
from .tools import calculate_utility_score, get_random_profile_id, get_profile_details
from .sub_agents.vetting import get_vetting_workflow

def get_broker_agent():
    # Instantiate fresh agents (Factory Pattern)
    synthesizer_agent = get_synthesizer_agent() 
    parser_agent = get_parser_agent()
    groom_rep = get_groom_rep()
    bride_rep = get_bride_rep()
    vetting_workflow = get_vetting_workflow() # Create a fresh instance

    vetting_pipeline = SequentialAgent(
        name="VettingPipeline",
        sub_agents=[
            parser_agent,         # Step 1: Extract IDs
            vetting_workflow,      # Step 2: Parallel Checks
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
        instruction="""You are the Chief Marriage Broker.

        **PHASE 1: VETTING**
        1. Call `VettingPipeline`.
        2. **CRITICAL STEP:** Analyze the final JSON verdict from the pipeline.
           - If the verdict contains the word 'FAIL', respond with the exact text: "VERDICT: MATCH REJECTED. Vetting failed due to critical risk." and STOP.
           - If the verdict contains the word 'PASS', respond with the exact text: "VERDICT: VETTING PASSED. PROCEEDING TO NEGOTIATION."

        **PHASE 2: NEGOTIATION**
        1. Consult Reps (use AgentTools).
        2. Propose compromise.
        3. Verify with `calculate_utility_score`.
        4. If Score > 60, declare MATCH SUCCESSFUL.
        """
    )
