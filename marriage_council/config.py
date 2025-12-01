import os
import logging
from dataclasses import dataclass
import google.auth

# Logging Setup
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google.adk").setLevel(logging.ERROR)

# --- AUTH SETUP: ROBUST DETECTION ---
# 1. Try getting from Environment Variable first (Most reliable in Cloud Shell)
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

# 2. If not in env, try Google Auth Default
if not project_id:
    try:
        _, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        print("⚠️ Auth Warning: Default credentials not found.")
        print("   Please run 'gcloud auth application-default login' for local development.")

# 3. Configure Environment
if project_id:
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    print(f"✅ Auth: Using Vertex AI (Project: {project_id})")
else:
    print("⚠️ Auth Warning: Could not determine Project ID.")
    print("   Please run: export GOOGLE_CLOUD_PROJECT=your-project-id")

@dataclass
class AgentConfig:
    db_name: str = "matrimony_council.sqlite"
    model_fast: str = "gemini-2.5-flash"
    model_smart: str = "gemini-2.5-pro"

# CRITICAL FIX: Ensure 'conf' is defined at the module level
conf = AgentConfig()
