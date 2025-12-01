import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from marriage_council.agent import root_agent

async def main():
    print("🧪 Running Integration Test...")
    session = InMemorySessionService()
    await session.create_session("test_app", "test_user", "test_sess_1")
    
    runner = Runner(agent=root_agent, app_name="test_app", session_service=session)
    
    # Scenario: Run full flow
    prompt = "Identify Groom G-1 and Bride B-1. Run full vetting and negotiation."
    print(f"Input: {prompt}")
    
    async for event in runner.run_async(
        user_id="test_user", session_id="test_sess_1", 
        new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
    ):
        if event.is_final_response() and event.content:
            print(f"🤖 Agent: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
