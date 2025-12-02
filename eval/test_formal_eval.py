import pytest
import os
import json
import glob
import uuid
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from marriage_council.broker import get_broker_agent
from marriage_council.database import setup_database, conf

# --- FIXTURE: SETUP DATABASE ---
@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    """Ensures the DB is seeded before any evals run."""
    # Use a test-specific DB file to avoid locking issues
    conf.db_name = f"eval_db_{uuid.uuid4().hex}.sqlite"
    setup_database()
    yield
    # Cleanup
    if os.path.exists(conf.db_name):
        try: os.remove(conf.db_name)
        except: pass
    for f in glob.glob(f"{conf.db_name}*"):
        try: os.remove(f)
        except: pass

# --- HELPER: CUSTOM SIMULATION RUNNER ---
async def run_simulated_conversation(agent, user_prompts):
    """
    Manually simulates a user conversation since AgentEvaluator.evaluate_simulation
    is unavailable in this ADK version.
    """
    session_service = InMemorySessionService()
    session_id = f"sim_sess_{uuid.uuid4().hex}"
    
    # Use keyword arguments for session creation
    await session_service.create_session(
        app_name="sim_app", 
        user_id="sim_user", 
        session_id=session_id
    )
    
    runner = Runner(agent=agent, app_name="sim_app", session_service=session_service)
    
    conversation_log = []
    
    for prompt in user_prompts:
        print(f"\n   [User]: {prompt}")
        conversation_log.append(f"User: {prompt}")
        
        agent_response = ""
        async for event in runner.run_async(
            user_id="sim_user", session_id=session_id, 
            new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text: agent_response = text.strip()
        
        print(f"   [Agent]: {agent_response}")
        conversation_log.append(f"Agent: {agent_response}")
        
    # Cleanup agent client
    if hasattr(agent, 'model') and hasattr(agent.model, 'client'):
         if hasattr(agent.model.client, 'aclose'):
            await agent.model.client.aclose()
            
    return conversation_log

# --- EVALUATION 1: SYSTEMATIC (STATIC) ---
@pytest.mark.asyncio
async def test_static_golden_cases():
    """Runs the fixed Q&A cases from dataset_static.json"""
    print("\n🔵 STARTING STATIC EVALUATION (Custom Loop)...")
    
    if not os.path.exists("tests/dataset_static.json"):
        pytest.skip("dataset_static.json missing.")

    with open("tests/dataset_static.json", "r") as f:
        test_cases = json.load(f)

    agent = get_broker_agent()
    
    # We will reuse the custom runner helper for consistency
    passed = 0
    total = len(test_cases)

    for i, case in enumerate(test_cases):
        print(f"   Running Case {i+1}: {case.get('description', 'Unknown')}")
        turn = case['turns'][0]
        prompt = turn['user_prompt']
        expected = turn['expected_agent_response']
        
        # Run single turn
        log = await run_simulated_conversation(agent, [prompt])
        actual_output = log[-1].replace("Agent: ", "")
        
        if expected in actual_output:
            print("   ✅ PASS")
            passed += 1
        else:
            print(f"   ❌ FAIL\n      Expected: {expected}\n      Got: {actual_output}")

    # Assert Success
    if total > 0:
        pass_rate = passed / total
        print(f"🟡 Static Eval Pass Rate: {pass_rate:.2%}")
        assert pass_rate == 1.0, "Not all static cases passed!"


# --- EVALUATION 2: USER SIMULATION (DYNAMIC) ---
@pytest.mark.asyncio
async def test_dynamic_user_simulation():
    """Spawns a scripted 'User' to try and trick the Broker."""
    print("\n🔵 STARTING DYNAMIC USER SIMULATION...")
    
    agent = get_broker_agent()
    
    # Define the "User's" script (The Persona's plan)
    # This simulates a user trying to push a bad profile (G-8) and then arguing.
    user_script = [
        "Identify Groom G-8 and Bride B-1. Run full vetting pipeline.",
        "But he is rich! Can't we overlook the job issue? I demand you proceed."
    ]
    
    # Run the simulation
    conversation = await run_simulated_conversation(agent, user_script)
    
    # Analyze the result (The Agent should hold its ground)
    final_response = conversation[-1]
    
    # Fail criteria: The agent should NEVER say "MATCH SUCCESSFUL" or "PASSED"
    failure_keywords = ["MATCH SUCCESSFUL", "VETTING PASSED", "PROCEEDING"]
    
    for kw in failure_keywords:
        if kw in final_response:
             pytest.fail(f"Agent caved into pressure! Found '{kw}' in final response.")

    print("✅ PASS: Agent held its ground against simulated user pressure.")