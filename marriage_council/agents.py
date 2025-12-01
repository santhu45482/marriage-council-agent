from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from .config import conf
from .tools import *
from pydantic import BaseModel, Field

# --- Pydantic Schema for Synthesizer Output ---
class VettingVerdict(BaseModel):
    """The clean, structured decision for the Broker."""
    status: str = Field(..., description="Must be 'PASS' or 'FAIL'.")
    summary: str = Field(..., description="A brief reason for the PASS/FAIL verdict.")

# --- Context Parser Agent ---
def get_parser_agent():
    return LlmAgent(
        name="parser_agent",
        model=Gemini(model=conf.model_fast),
        instruction="""You are the Data Extractor. 
        Check the history for profile IDs (G-X, B-X). 
        Output ONLY the IDs found, or "None".""",
        output_key="extracted_ids"
    )

# 1. Vetting Specialists
def get_vetting_council():
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
    return ParallelAgent(
        name="vetting_council",
        sub_agents=[detective, astrologer],
        description="Runs background and astrology checks simultaneously."
    )

def get_synthesizer_agent():
    return LlmAgent(
        name="synthesizer_agent",
        model=Gemini(model=conf.model_smart),
        instruction="""You are the Synthesis Agent. You receive outputs from the Detective and Astrologer. 
        Your task is to provide a single, clean JSON verdict.
        1. If the Detective reports 'CRITICAL FAIL' OR Astrologer reports 'WARNING' (score < 18): set status to 'FAIL'.
        2. Otherwise, set status to 'PASS'.
        3. STRICTLY output JSON matching the VettingVerdict schema.
        """,
        output_schema=VettingVerdict,
        output_key="verdict"
    )

def get_groom_rep():
    return LlmAgent(
        name="groom_rep",
        model=Gemini(model=conf.model_fast),
        tools=[FunctionTool(get_profile_details)],
        instruction="Represent Groom. Prefer his location. Be stubborn but polite. Use tool `get_profile_details`."
    )

def get_bride_rep():
    return LlmAgent(
        name="bride_rep",
        model=Gemini(model=conf.model_fast),
        tools=[FunctionTool(get_profile_details)],
        instruction="Represent Bride. Career is non-negotiable. Prefer her location. Use tool `get_profile_details`."
    )

def get_judge_agent():
    return LlmAgent(
        name="judge_agent",
        model=Gemini(model=conf.model_smart),
        instruction="Evaluate the final deal string. Rate 1-5 on Fairness."
    )
