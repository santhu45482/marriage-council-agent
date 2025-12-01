import asyncio
import unittest
import gc
import os
import uuid
import warnings
import json
import sqlite3
from unittest.mock import patch, MagicMock

# Suppress warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message="Event loop is closed")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# Import system components
from marriage_council.broker import get_broker_agent
from marriage_council.database import setup_database
from marriage_council.config import conf
from marriage_council.tools import perform_background_check

# --- HELPER: Mock Gemini Class ---
# We inherit from Gemini so Pydantic accepts it as a valid model
class MockGemini(Gemini):
   # Private field to store our canned response
   _response_text: str = ""

   def __init__(self, response_text: str):
       # Initialize the parent Gemini model normally
       super().__init__(model=conf.model_fast)
       self._response_text = response_text
      
       # Prevent "Event loop closed" errors by mocking the client cleanup
       # We replace the internal client's aclose with a no-op future
       self.client = MagicMock()
       f = asyncio.Future()
       f.set_result(None)
       self.client.aclose = MagicMock(return_value=f)

   # We override the generation method to return our fixed JSON
   async def generate_content_async(self, *args, **kwargs):
       print(f"      [MockGemini] Generating: {self._response_text}")
       yield types.GenerateContentResponse(
           candidates=[types.Candidate(
               content=types.Content(parts=[types.Part(text=self._response_text)])
           )]
       )

# --- HELPER: Agent Builder ---
def build_mock_vetting_agent(verdict_status):
   """Creates an Agent using our compliant MockGemini model."""
   response_json = json.dumps({
       "status": verdict_status,
       "summary": f"Mocked {verdict_status} decision."
   })
   # PASS: We use a real Agent with a valid subclass of Gemini
   return Agent(
       name="VettingPipeline",
       model=MockGemini(response_json)
   )


class AgentLogicTest(unittest.IsolatedAsyncioTestCase):

   async def asyncSetUp(self):
       self.test_db_file = f"test_db_{uuid.uuid4().hex}.sqlite"
       self.original_db_name = conf.db_name
       conf.db_name = self.test_db_file
       setup_database()
      
       self.session_service = InMemorySessionService()
       self.session_id = "test_sess_1"
      
       await self.session_service.create_session(
           app_name="test_app",
           user_id="test_user",
           session_id=self.session_id
       )

   async def asyncTearDown(self):
       conf.db_name = self.original_db_name
       gc.collect()
       if os.path.exists(self.test_db_file):
           try:
               os.remove(self.test_db_file)
           except OSError: pass

   # --- 1. UNIT TEST: DETECTIVE LOGIC ---
   async def test_detective_tool_logic(self):
       print("\n🔵 TEST: Detective Tool Logic (Direct DB Check)")
      
       # G-8: Force "Fake Job"
       conn = sqlite3.connect(conf.db_name)
       conn.execute("UPDATE profiles SET risk_factor='Fake Job' WHERE id='G-8'")
       conn.commit()
       conn.close()
      
       result_fail = perform_background_check("G-8")
       print(f"   Checked G-8 (Fake Job): {result_fail}")
       self.assertEqual(result_fail, "RISK_FOUND", "Detective failed to catch Fake Job!")

       # G-1: Force "Clean"
       conn = sqlite3.connect(conf.db_name)
       conn.execute("UPDATE profiles SET risk_factor='Clean' WHERE id='G-1'")
       conn.commit()
       conn.close()

       result_pass = perform_background_check("G-1")
       print(f"   Checked G-1 (Clean): {result_pass}")
       self.assertEqual(result_pass, "CLEAN", "Detective falsely flagged a clean profile!")
       print("✅ PASS")

   # --- 2. INTEGRATION TEST: BROKER DECISION (PASS) ---
   async def test_broker_handling_pass(self):
       print("\n🔵 TEST: Broker Handling of PASS Verdict")
      
       mock_agent = build_mock_vetting_agent("PASS")
      
       with patch('marriage_council.broker.SequentialAgent', return_value=mock_agent):
           await self.run_broker_scenario(
               "Identify Groom G-1 and Bride B-1. Run vetting.",
               "VERDICT: VETTING PASSED"
           )

   # --- 3. INTEGRATION TEST: BROKER DECISION (FAIL) ---
   async def test_broker_handling_fail(self):
       print("\n🔵 TEST: Broker Handling of FAIL Verdict")
      
       mock_agent = build_mock_vetting_agent("FAIL")
      
       with patch('marriage_council.broker.SequentialAgent', return_value=mock_agent):
           await self.run_broker_scenario(
               "Identify Groom G-8 and Bride B-1. Run vetting.",
               "VERDICT: MATCH REJECTED"
           )

   # --- 4. INTEGRATION TEST: NEGOTIATION (Success) ---
   async def test_negotiation_success(self):
       print("\n🔵 TEST: Negotiation Success")
       prompt = """
       Phase 1 passed. Couple details: Groom (Location: Delhi, Job: Banker), Bride (Location: Bangalore, Career: Doctor).
       Propose the optimal compromise: Live in Delhi, Bride keeps her Doctor career.
       Verify the final utility score to finalize the deal.
       """
       await self.run_broker_scenario(prompt, "MATCH SUCCESSFUL")

   # --- 5. INTEGRATION TEST: NEGOTIATION (Failure) ---
   async def test_negotiation_failure(self):
       print("\n🔵 TEST: Negotiation Failure")
       prompt = """
       Phase 1 passed. Couple details: Groom (Location: Delhi, Job: Banker), Bride (Location: Bangalore, Career: Doctor).
       Propose the optimal compromise: Live in Mumbai, Bride quits her Doctor career.
       Verify the final utility score to finalize the deal.
       """
       await self.run_broker_scenario(prompt, "NEGOTIATION FAILED")


   # --- HELPER RUNNER ---
   async def run_broker_scenario(self, prompt, expected_output):
       fresh_agent = get_broker_agent()
       runner = Runner(agent=fresh_agent, app_name="test_app", session_service=self.session_service)
      
       final_response = "NO RESPONSE"
       try:
           async for event in runner.run_async(
               user_id="test_user", session_id=self.session_id,
               new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
           ):
               if event.get_function_calls():
                    print(f"   ⚙️ TOOL CALL: {event.get_function_calls()[0].name}")

               if event.content and event.content.parts:
                   text = event.content.parts[0].text
                   if text:
                       final_response = text.strip()
                       log_text = (text[:70] + '..') if len(text) > 70 else text
                       print(f"   🗣️ AGENT: {log_text}")
       finally:
           try:
               # Cleanup using the standard ADK model interface
               if hasattr(fresh_agent, 'model') and hasattr(fresh_agent.model, 'client'):
                    if hasattr(fresh_agent.model.client, 'aclose'):
                       await fresh_agent.model.client.aclose()
               del fresh_agent
               del runner
               gc.collect()
           except: pass
      
       print(f"   Goal: '{expected_output}'")
       print(f"   Got:  '{final_response}'")
       self.assertIn(expected_output, final_response)
       print("✅ PASS")

if __name__ == "__main__":
   unittest.main(argv=['first-arg-is-ignored'], exit=False)
