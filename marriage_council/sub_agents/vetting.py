from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from ..config import conf
from ..tools import perform_background_check, check_horoscope_compatibility

def get_vetting_workflow():
    """Factory function to create a fresh vetting agent."""
    detective = LlmAgent(
        name="detective_agent",
        model=Gemini(model=conf.model_fast),
        tools=[FunctionTool(perform_background_check)],
        instruction="Receive IDs. Check background using tool `perform_background_check`. If 'High Debt' or 'Fake Job', report CRITICAL FAIL."
    )
    astrologer = LlmAgent(
        name="astrologer_agent",
        model=Gemini(model=conf.model_fast),
        tools=[FunctionTool(check_horoscope_compatibility)],
        instruction="Extract signs. Check compatibility using tool `check_horoscope_compatibility`. If score < 18, warn broker."
    )
    return ParallelAgent(name="vetting_council", sub_agents=[detective, astrologer])