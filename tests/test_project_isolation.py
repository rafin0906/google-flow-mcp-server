import json
import sys
from pathlib import Path

# Insert parent directory so 'app' can be imported correctly
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from app.services.db_handler import save_project_record, update_project_record, get_latest_project_record
from app.boss_functions.poster_generator import generate_poster
from app.boss_functions.poster_editor import edit_poster
from app.boss_functions.poster_ratio_editor import change_ratio_and_download
from app.config import DB_FILE

class DummyPage:
    def goto(self, url, **kwargs):
        print(f"*** ABORTING TEST: DummyPage.goto called with url={url} ***")
        raise Exception(f"DummyPage navigation intercepted! URL: {url}")

def run_test_7():
    print("--- Test 7: Project-level two-session isolation ---")
    
    session_a = "session-A-uuid"
    session_b = "session-B-uuid"
    
    print("\n[Step 2] Session A creates project A")
    save_project_record(
        project_url="https://labs.google/fx/tools/flow/project-A",
        ratio="16:9",
        project_id="proj_A123",
        session_id=session_a
    )
    
    print("\n[Step 3] Session B creates project B")
    save_project_record(
        project_url="https://labs.google/fx/tools/flow/project-B",
        ratio="1:1",
        project_id="proj_B456",
        session_id=session_b
    )
    
    print("\n[Step 4] Checking db/projects.json on disk:")
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for proj in data.get("projects", [])[-2:]:
            print(f"Record found: session_id={proj.get('session_id')}, project_url={proj.get('project_url')}, ratio={proj.get('ratio')}")
            
    print("\n[Step 5] Call get_latest_project_record for Session A:")
    rec_a = get_latest_project_record(session_id=session_a)
    print(f"Returned: {rec_a.get('project_url') if rec_a else None}")
    assert rec_a and rec_a["project_url"] == "https://labs.google/fx/tools/flow/project-A", "Session A got wrong record!"
    
    print("\n[Step 6] Call get_latest_project_record for Session B:")
    rec_b = get_latest_project_record(session_id=session_b)
    print(f"Returned: {rec_b.get('project_url') if rec_b else None}")
    assert rec_b and rec_b["project_url"] == "https://labs.google/fx/tools/flow/project-B", "Session B got wrong record!"
    
    print("\n[Step 7] Call generate_poster with session_id=session-A-uuid and NO project_url override")
            
    try:
        generate_poster(session_id=session_a, project_url=None, page=DummyPage())
    except Exception as e:
        print(f"\nCaught Exception intentionally to abort browser: {e}")
        
    print("\n--- Test 7 complete ---")


def run_tests_8_9():
    print("\n--- Test 8: Session Isolation for edit_poster & ratio_editor ---")
    
    session_a = "session-A-uuid-2"
    session_b = "session-B-uuid-2"
    
    print("\n[Setup] Create projects & set image_edit_page_urls")
    save_project_record(project_url="url-A", session_id=session_a)
    update_project_record(project_url="url-A", image_edit_page_url="edit-url-A", session_id=session_a)
    
    save_project_record(project_url="url-B", session_id=session_b)
    update_project_record(project_url="url-B", image_edit_page_url="edit-url-B", session_id=session_b)
    
    print("\n[Test 8.1] Call edit_poster for Session A")
    try:
        edit_poster(session_id=session_a, image_edit_page_url=None, page=DummyPage())
    except Exception as e:
        print(f"Caught Exception intentionally: {e}")
        
    print("\n[Test 8.2] Call change_ratio_and_download for Session B")
    try:
        change_ratio_and_download(session_id=session_b, edit_url=None, page=DummyPage())
    except Exception as e:
        print(f"Caught Exception intentionally: {e}")
        
    
    print("\n--- Test 9: Ownership-Mismatch Guard ---")
    
    print("\n[Test 9.1] Session B attempts to hack Session A's project by URL")
    res = update_project_record(project_url="url-A", session_id=session_b, status="hacked")
    print(f"Update Result (should be None): {res}")
    assert res is None, "Security bypass! Session B modified Session A's project!"
    
    print("\n[Test 9.2] Verify on disk that Session A's project is untouched")
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        proj_a = None
        for p in data.get("projects", []):
            if p.get("project_url") == "url-A":
                proj_a = p
                
    print(f"Session A Project Status on disk: {proj_a.get('status')}")
    assert proj_a.get("status") != "hacked", "Status was changed on disk!"
    print("\n--- Tests 8 and 9 complete ---")

def cleanup_test_records():
    print("\n=======================================")
    print("CLEANING UP TEST RECORDS")
    print("=======================================")
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        original_count = len(data.get("projects", []))
        
        # Filter out all records created by our hardcoded test sessions
        test_sessions = {"session-A-uuid", "session-B-uuid", "session-A-uuid-2", "session-B-uuid-2"}
        filtered_projects = [
            p for p in data.get("projects", [])
            if p.get("session_id") not in test_sessions
        ]
        
        data["projects"] = filtered_projects
        
        # Save directly to bypass save_project_record which appends
        from app.services.db_handler import save_db
        save_db(data)
        
        print(f"Removed {original_count - len(filtered_projects)} test records from DB.")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    run_test_7()
    run_tests_8_9()
    cleanup_test_records()

if __name__ == "__main__":
    main()
