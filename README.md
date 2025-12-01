# 💍 The Marriage Council AI (Multi-Agent System)

This project implements a production-ready **Multi-Agent System** using the **Google Agent Development Kit (ADK)** to automate the complex, multi-stage process of arranged matrimonial negotiation and verification.

It operates in a two-phase hierarchy: Vetting (objective verification) followed by Negotiation (subjective compromise).

-----

## 1\. System Architecture

The core architecture is built around a centralized **Broker Agent** that orchestrates a workflow composed of specialized sub-agents running in parallel and sequence.

### Agent Hierarchy

| Agent Role | Type | Primary Function |
| :--- | :--- | :--- |
| **`marriage_broker_agent`** | Root/Orchestrator | Manages the full flow (Vetting → Negotiation). Makes the final decision based on the Utility Score. |
| **`VettingPipeline`** | Sequential/Parallel | Executes parallel checks (Detective & Astrologer) and synthesizes the final **PASS/FAIL** verdict in JSON format. |
| **`detective_agent`** | LlmAgent | Executes the **`perform_background_check`** tool against the database. |
| **`groom_rep` / `bride_rep`** | LlmAgents | Persona-based negotiators focused on specific demands (Location preference, Career negotiation). |


### Key Tools

The system relies on custom Python `FunctionTool`s for deterministic logic:

  * **`perform_background_check`**: Checks the SQLite database for critical risks (`Fake Job`, `High Debt`).
  * **`calculate_utility_score`**: Quantifies the viability of the final compromise (Score \> 60 is successful).
  * **`log_event`**: Records agent actions and results to the `agent_logs` SQLite table for observability.

-----

## 2\. Setup and Execution

### Prerequisites

  * Python 3.10+
  * A configured **Google Cloud Project** and authenticated `gcloud` credentials.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone [YOUR_REPO_URL]
    cd marriage-council-agent
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```


### Execution

1.  **Start the Application:**
    The project runs as a Streamlit web interface, which automatically initializes and seeds the `matrimony_council.sqlite` database on first run.

    ```bash
    streamlit run marriage_council/app.py
    ```

2.  **Run Evaluation (Testing):**
    The system includes robust integration tests to verify the core logical decisions.

    ```bash
    # Run all integration tests (Vetting, Negotiation, Detective logic)
    python -m tests.test_agent
    ```

-----
3. **Deployment(cloud):**
   you can Interacting with cloud web app deployed in Google cloud.

   (https://marriage-council-agent-265055087845.us-central1.run.app/)

## 3\. Project Structure

```
.
├── marriage_council/
│   ├── sub_agents/
│   ├── tools.py          # Custom FunctionTools
│   ├── database.py       # SQLite setup and logging
│   ├── broker.py         # The Root Agent logic
│   └── app.py            # Streamlit UI
├── tests/
│   └── test_agent.py     # Integration Test Suite
├── assets/
│   └── architecture-diagram.png
└── requirements.txt
```
## 4\. Cite US
   To cite this project.
   '''
   {
   author = {Santhosha S R},
   journal = {https://github.com/santhu45482/marriage-council-agent/},
   month = {12},
   title = {{The Marriage Council AI (Multi-Agent System)
 }},
   year = {2025}
   }
   '''
