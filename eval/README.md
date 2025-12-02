🧪 Automated Agent Evaluation Framework

This directory contains the test suite for systematically evaluating the Marriage Council Agent. It uses pytest and the Google ADK to run both static golden test cases and dynamic user simulations.

📂 Structure

dataset_static.json: The "Golden Dataset" containing fixed user prompts and expected agent responses (e.g., "Identify Groom G-1...").

sim_config.yaml: Configuration for the User Simulation (Dynamic Evaluation), defining the persona of a desperate user trying to trick the agent.

test_formal_eval.py: The main Pytest script that:

Sets up a temporary, isolated SQLite database for each test run.

Runs the Static Evaluation (checking if the agent passes G-1 and fails G-8 correctly).

Runs the Dynamic Simulation (spawning an AI user to argue with the Broker).

conftest.py: Pytest configuration file that handles global setup and teardown logic.

🚀 How to Run Evaluations

Prerequisites

Ensure you have installed the project dependencies:

pip install -r requirements.txt


Running the Tests

To execute the full evaluation suite, run the following command from the root of your project:

python -m pytest eval/test_formal_eval.py


Understanding the Output

✅ PASS: The agent responded exactly as expected (e.g., rejected a risky profile or approved a valid one).

❌ FAIL: The agent's logic drifted (e.g., it approved a "Fake Job" profile or failed to negotiate).

🛠️ modifying Tests

To add more static cases (e.g., testing a specific location mismatch), edit dataset_static.json.

To change the simulated user's behavior (e.g., make them more aggressive), edit the persona in sim_config.yaml.