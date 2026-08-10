import asyncio
import sys
from pathlib import Path

# Insert parent directory so 'app' can be imported correctly
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

from app.mcp.server import tool_input_images, tool_generate_poster
from app.boss_functions.poster_generator import generate_poster
from app.services.clipboard_handler import clear_input_images
from app.config import INPUT_IMAGES_DIR

# ---------------------------------------------------------
# TESTS 1-4: MCP Protocol Level Tests
# ---------------------------------------------------------
async def run_mcp_tests():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("=======================================")
                print("Setting up: Creating Project")
                print("=======================================")
                res_create = await session.call_tool("tool_create_project", {"headless": True})
                print("Create Project result:", res_create.content[0].text)
                
                print("\n=======================================")
                print("TEST 1: Single session, with images")
                print("=======================================")
                dummy_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAADAAFAAEEVWqQAAAAASUVORK5CYII="
                res1 = await session.call_tool("tool_input_images", {
                    "images_b64": [{"name": "test1.png", "mime": "image/png", "b64": dummy_png_b64}]
                })
                print("Upload result:", res1.content[0].text)
                
                print("\nGenerating poster with image...")
                res2 = await session.call_tool("tool_generate_poster", {
                    "prompt": "a simple test poster",
                    "headless": True
                })
                print("Generate result:", res2.content[0].text)
                
                print("\n=======================================")
                print("TEST 2: Zero images (text-only)")
                print("=======================================")
                res3 = await session.call_tool("tool_generate_poster", {
                    "prompt": "a text only test poster",
                    "headless": True
                })
                print("Generate text-only result:", res3.content[0].text)
                
                print("\n=======================================")
                print("TEST 3: Invalid inputs")
                print("=======================================")
                try:
                    res4 = await session.call_tool("tool_input_images", {
                        "images_b64": [{"name": "../../evil.png", "mime": "image/png", "b64": dummy_png_b64}]
                    })
                    print("evil.png result:", res4.content[0].text)
                except Exception as e:
                    print(f"evil.png properly raised an exception: {e}")
                
                try:
                    res5 = await session.call_tool("tool_input_images", {
                        "images_b64": [{"name": "test.exe", "mime": "application/x-msdownload", "b64": dummy_png_b64}]
                    })
                    print("test.exe result:", res5.content[0].text)
                except Exception as e:
                    print(f"test.exe properly raised an exception: {e}")

                print("\n=======================================")
                print("TEST 4: Missing session")
                print("=======================================")
                print("(Calling functions directly to bypass MCP client's automatic context injection)")
                
                try:
                    await tool_input_images([{"name": "test.png", "mime": "image/png", "b64": dummy_png_b64}], ctx=None)
                    print("FAIL: tool_input_images should have raised an exception!")
                except Exception as e:
                    print(f"tool_input_images correctly raised exception: {e}")
                    
                try:
                    await tool_generate_poster(prompt="test", ctx=None)
                    print("FAIL: tool_generate_poster should have raised an exception!")
                except Exception as e:
                    print(f"tool_generate_poster correctly raised exception: {e}")

    except Exception as e:
        print(f"Global Error in MCP tests: {e}")

# ---------------------------------------------------------
# TEST 5: Two-session isolation
# ---------------------------------------------------------
class MockContext:
    def __init__(self, session_id):
        self.session_id = session_id

async def run_isolation_tests():
    print("\n=======================================")
    print("TEST 5: Two-session file isolation")
    print("=======================================")
    
    session_a_uuid = "session-A-uuid"
    session_b_uuid = "session-B-uuid"
    
    ctx_a = MockContext(session_a_uuid)
    ctx_b = MockContext(session_b_uuid)
    
    dummy_a_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAADAAFAAEEVWqQAAAAASUVORK5CYII="
    dummy_b_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAAXNSR0IArs4c6QAAABdJREFUGFdj/M/A8J+BgYGB8T8DgwADAA+JAgH9zH44AAAAAElFTkSuQmCC"

    try:
        print("Uploading imageA.png to Session A...")
        await tool_input_images([{"name": "imageA.png", "mime": "image/png", "b64": dummy_a_b64}], ctx=ctx_a)
        
        print("Uploading imageB.png to Session B...")
        await tool_input_images([{"name": "imageB.png", "mime": "image/png", "b64": dummy_b_b64}], ctx=ctx_b)
    except Exception as e:
        print(f"Error during uploads: {e}")

    dir_a = INPUT_IMAGES_DIR / session_a_uuid
    dir_b = INPUT_IMAGES_DIR / session_b_uuid
    
    print(f"\nChecking disk BEFORE generation:")
    print(f"Session A dir exists? {dir_a.exists()}")
    if dir_a.exists():
        print(f"Session A files: {[f.name for f in dir_a.iterdir()]}")
        
    print(f"Session B dir exists? {dir_b.exists()}")
    if dir_b.exists():
        print(f"Session B files: {[f.name for f in dir_b.iterdir()]}")

    print("\nCalling generate_poster for Session A...")
    try:
        res_a = await asyncio.to_thread(generate_poster, prompt="session A test", session_id=session_a_uuid, headless=True)
        print("Session A generation completed.")
    except Exception as e:
        print(f"Generate error: {e}")

    print("\nChecking disk AFTER Session A generation:")
    print(f"Session A dir exists? {dir_a.exists()}")
    if dir_a.exists():
        files_a = [f.name for f in dir_a.iterdir()]
        print(f"Session A files: {files_a}")
    else:
        print("-> SUCCESS: Session A directory is COMPLETELY REMOVED.")

    print(f"Session B dir exists? {dir_b.exists()}")
    if dir_b.exists():
        files_b = [f.name for f in dir_b.iterdir()]
        print(f"Session B files: {files_b}")
        if "imageB.png" in files_b:
            print("-> SUCCESS: Session B directory and imageB.png are UNTOUCHED.")
        else:
            print("-> FAIL: imageB.png is missing!")
    else:
        print("-> FAIL: Session B directory was incorrectly removed!")

# ---------------------------------------------------------
# TEST 6: Crash-recovery / Stale Session Cleanup
# ---------------------------------------------------------
def run_cleanup_tests():
    print("\n=======================================")
    print("TEST 6: Crash-recovery / Stale Session Cleanup")
    print("=======================================")
    
    stale_1 = INPUT_IMAGES_DIR / "fake-session-999"
    stale_2 = INPUT_IMAGES_DIR / "another-stale-session"
    
    stale_1.mkdir(parents=True, exist_ok=True)
    stale_2.mkdir(parents=True, exist_ok=True)
    
    with open(stale_1 / "junk1.png", "w") as f:
        f.write("dummy bytes")
        
    with open(stale_2 / "junk2.png", "w") as f:
        f.write("more dummy bytes")
        
    print("Disk state BEFORE cleanup:")
    print(f"{stale_1.name} exists? {stale_1.exists()} | Files: {[f.name for f in stale_1.iterdir()] if stale_1.exists() else []}")
    print(f"{stale_2.name} exists? {stale_2.exists()} | Files: {[f.name for f in stale_2.iterdir()] if stale_2.exists() else []}")
    
    print("\nCalling clear_input_images() ...")
    clear_input_images()
    
    print("\nDisk state AFTER cleanup:")
    print(f"{stale_1.name} exists? {stale_1.exists()}")
    print(f"{stale_2.name} exists? {stale_2.exists()}")
    
    if not stale_1.exists() and not stale_2.exists():
        print("-> SUCCESS: All stale session folders were completely removed.")
    else:
        print("-> FAIL: Some stale folders were not removed.")

async def main():
    await run_mcp_tests()
    await run_isolation_tests()
    run_cleanup_tests()

if __name__ == "__main__":
    asyncio.run(main())
