from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from ..config import conf
from ..tools import get_profile_details

groom_rep = LlmAgent(
    name="groom_rep",
    model=Gemini(model=conf.model_fast),
    tools=[FunctionTool(get_profile_details)],
    instruction="Represent Groom. Prefer his location. Use ."
)

bride_rep = LlmAgent(
    name="bride_rep",
    model=Gemini(model=conf.model_fast),
    tools=[FunctionTool(get_profile_details)],
    instruction="Represent Bride. Career is non-negotiable. Use ."
)
