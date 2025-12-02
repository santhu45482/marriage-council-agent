import pytest
import os
import glob
import uuid
from marriage_council.database import setup_database, conf

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Global setup for the entire test session.
    Ensures a fresh database is available for evaluations.
    """
    # Use a unique DB file for this test run to avoid locking/conflicts
    test_db_name = f"eval_db_{uuid.uuid4().hex}.sqlite"
    conf.db_name = test_db_name
    
    # Initialize the DB with seed data
    if os.path.exists(test_db_name):
        try: os.remove(test_db_name)
        except: pass
    setup_database()
    
    yield
    
    # Teardown: Cleanup the DB file after all tests are done
    if os.path.exists(test_db_name):
        try: os.remove(test_db_name)
        except: pass
    # Clean up any journal/wal files
    for f in glob.glob(f"{test_db_name}*"):
        try: os.remove(f)
        except: pass