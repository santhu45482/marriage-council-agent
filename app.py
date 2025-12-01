import streamlit as st
import asyncio
import sqlite3
import pandas as pd
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from marriage_council.broker import get_broker_agent
from marriage_council.config import conf
from marriage_council.database import setup_database

st.set_page_config(page_title="Marriage Council AI", layout="wide", page_icon="💍")

# --- 1. INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_service" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()
    st.session_state.session_id = "session_v1"
    
    async def init_session():
        await st.session_state.session_service.create_session(
            app_name="MarriageApp", user_id="user", session_id=st.session_state.session_id
        )
    asyncio.run(init_session())

setup_database()

# --- 2. GLOBAL FUNCTION: RUN AGENT LOGIC ---
async def run_agent(input_prompt):
    # FIX: Create Agent FRESH inside the loop
    fresh_agent = get_broker_agent()
    
    local_runner = Runner(
        agent=fresh_agent,
        app_name="MarriageApp",
        session_service=st.session_state.session_service
    )
    
    st.session_state.messages.append({"role": "user", "content": input_prompt})
    
    with st.chat_message("user"):
        st.markdown(input_prompt)
        
    with st.chat_message("assistant"):
        response_container = st.empty()
        response_data = [""]
        
        msg_content = types.Content(role="user", parts=[types.Part(text=input_prompt)])
        
        async for event in local_runner.run_async(
            user_id="user", session_id=st.session_state.session_id, new_message=msg_content
        ):
            if event.get_function_calls():
                fn = event.get_function_calls()[0]
                with st.status(f"⚙️ Calling Tool: {fn.name}...", expanded=False):
                    st.write(f"Arguments: {fn.args}")
            
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    response_data[0] = text
                    response_container.markdown(response_data[0])
        
    st.session_state.messages.append({"role": "assistant", "content": response_data[0]})


# --- 3. UI LAYOUT ---
st.title("💍 The Marriage Council AI")
st.markdown("A **Multi-Agent System** that vets, negotiates, and mediates arranged marriages.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Negotiation Console")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask the broker..."):
        asyncio.run(run_agent(prompt))


# --- 4. GUIDED WORKFLOW BUTTONS ---
st.markdown("---")
st.subheader("Guided Workflow")
colA, colB, colC = st.columns(3)

with colA:
    if st.button("1. IDENTIFY & VET COUPLE", help="Finds random couple and runs parallel background checks."):
        asyncio.run(run_agent("Find a random couple and run the full vetting pipeline."))

with colB:
    if st.button("2. START NEGOTIATION", help="Consults Groom/Bride reps to gather their initial demands."):
        asyncio.run(run_agent("Phase 1 passed. Consult the Groom and Bride representatives for their demands."))

with colC:
    if st.button("3. PROPOSE & FINALIZE DEAL", type="primary", help="Proposes the optimal compromise and verifies utility score."):
        asyncio.run(run_agent("Propose the optimal compromise and verify the final utility score to finalize the deal."))


with col2:
    st.subheader("📊 System Observability")
    if st.button("🔄 Refresh Logs"): 
        st.rerun()
        
    conn = sqlite3.connect(conf.db_name)
    
    st.write("**🕵️ Detective Logs**")
    try:
        logs = pd.read_sql("SELECT timestamp, details FROM agent_logs WHERE agent_name='Detective' ORDER BY id DESC LIMIT 5", conn)
        st.dataframe(logs, hide_index=True)
    except: st.write("No logs yet.")
    
    st.write("**💾 Database Profiles**")
    try:
        profiles = pd.read_sql("SELECT id, name, location, risk_factor FROM profiles LIMIT 5", conn)
        st.dataframe(profiles, hide_index=True)
    except: st.write("No profiles found.")
    conn.close()
