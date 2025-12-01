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
        # MODIFIED INSTRUCTION BELOW:
        instruction="""Receive IDs. Check background using tool `perform_background_check`. 
        If 'High Debt' or 'Fake Job' risk is found, respond ONLY with the exact, unique phrase: **DETECTIVE_CRITICAL_FAILURE**. 
        If clean, respond ONLY with: **DETECTIVE_CLEAN_PASS**."""
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

# marriage_council/agents.py (MODIFIED)

# marriage_council/agents.py (inside get_synthesizer_agent)

def get_synthesizer_agent():
    return LlmAgent(
        name="synthesizer_agent",
        model=Gemini(model=conf.model_smart),
        instruction="""You are the Synthesis Agent. Analyze the output from the Detective and Astrologer. 
        Your task is to provide a single, clean JSON verdict strictly matching the VettingVerdict schema.
        
        **CRITICAL RULE:**
        1. **IF the input contains 'DETECTIVE_CRITICAL_FAILURE' OR 'BAD_MATCH'**: set the 'status' field to **'FAIL'** in the JSON.
        2. OTHERWISE: set the 'status' field to **'PASS'**.
        3. Output ONLY the JSON object and no other text.""",
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
