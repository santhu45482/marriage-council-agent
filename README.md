# 💍 The Marriage Council (Modular Edition)
**Google AI Agents Capstone Project**

A production-grade multi-agent system for matrimonial negotiation, refactored for modularity and scalability.

## 🏗️ Architecture
- **Broker (Root):** Orchestrates the flow.
- **Vetting Council:** Parallel execution of Detective & Astrologer.
- **Negotiators:** Persona-based agents (Groom/Bride Reps).
- **Observability:** SQLite-backed logging and tracing.

## 📂 Structure
- `marriage_council/`: Core package.
  - `sub_agents/`: Modular agent definitions.
  - `tools.py`: Tool logic.
- `tests/`: Integration tests.
- `app.py`: Streamlit Interface.

## 🚀 Run
1. **Web UI:** `streamlit run app.py`
2. **Test Suite:** `python -m tests.test_agent`
