import os
import threading
import time
import pytest
import json
from app import app, BASE_DIR
from filelock import FileLock
from playwright.sync_api import Page, expect

# Use a separate test data file to avoid modifying production data
TEST_DATA_FILE = os.path.join(BASE_DIR, "data_test.json")
TEST_LOCK_FILE = f"{TEST_DATA_FILE}.lock"

@pytest.fixture(scope="session")
def flask_server():
    """Starts the Flask server in a separate thread for the duration of the test session."""
    # Set the environment variable for the app to use the test data file
    os.environ["DATA_FILE_PATH"] = TEST_DATA_FILE
    
    port = 5001
    app.config['TESTING'] = True
    
    server_thread = threading.Thread(target=lambda: app.run(port=port, debug=False, use_reloader=False))
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1.5)
    
    yield f"http://127.0.0.1:{port}"
    
    # Cleanup: Remove the test data file and its lock if they exist
    if os.path.exists(TEST_DATA_FILE):
        try:
            os.remove(TEST_DATA_FILE)
        except:
            pass
    if os.path.exists(TEST_LOCK_FILE):
        try:
            os.remove(TEST_LOCK_FILE)
        except:
            pass

@pytest.fixture(autouse=True)
def clean_data():
    """Ensures data_test.json is in a known baseline state before each test."""
    baseline = {
        "children": [
            {"id": 1, "name": "Child 1", "balance": 0.0, "is_active": True, "history": []},
            {"id": 2, "name": "Child 2", "balance": 0.0, "is_active": False, "history": []},
            {"id": 3, "name": "Child 3", "balance": 0.0, "is_active": False, "history": []},
            {"id": 4, "name": "Child 4", "balance": 0.0, "is_active": False, "history": []}
        ]
    }
    lock = FileLock(TEST_LOCK_FILE, timeout=5)
    with lock:
        with open(TEST_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
    yield

@pytest.fixture
def logged_in_page(page: Page, flask_server: str):
    """Fixture that provides a page object already logged into the app."""
    app_pin = os.getenv("APP_PIN", "1234")
    page.goto(flask_server)
    
    # If we are on login page, perform login
    if page.url.endswith("/login"):
        page.get_by_placeholder("****").fill(app_pin)
        page.get_by_role("button", name="Unlock Vault").click()
    
    # Ensure we are on dashboard before proceeding
    expect(page).to_have_url(f"{flask_server}/")
    return page
