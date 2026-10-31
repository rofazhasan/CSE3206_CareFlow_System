import subprocess
import time
import os
import signal
from PIL import Image

REPO_DIR = "/Users/md.rofazhasanrafiu/coding/CSE3206_CareFlow_System"
DOCS_DIR = os.path.join(REPO_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def capture_terminal_command(cmd, output_path, cols=115, rows=32, wait_sec=2.5):
    """Executes a command in a dedicated macOS Terminal window and takes a real screenshot."""
    print(f"\n--- Capturing Terminal for: {cmd} ---")
    script = f'''
    tell application "Terminal"
        activate
        set newTab to do script "cd {REPO_DIR} && clear && {cmd}"
        set current_win to front window
        set number of columns of current_win to {cols}
        set number of rows of current_win to {rows}
        set win_id to id of current_win
        return win_id
    end tell
    '''
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    win_id = res.stdout.strip()
    print(f"Terminal Window ID: {win_id}")
    time.sleep(wait_sec)
    
    # Capture window with window id using screencapture
    subprocess.run(["screencapture", f"-l{win_id}", "-o", output_path], check=True)
    print(f"Captured: {output_path} ({os.path.getsize(output_path)} bytes)")
    
    # Close window cleanly
    close_script = f'''
    tell application "Terminal"
        close window id {win_id}
    end tell
    '''
    subprocess.run(["osascript", "-e", close_script], capture_output=True)

def capture_fastapi_swagger(output_path):
    """Starts FastAPI in background, waits for Swagger UI to render, and takes real Chrome screenshot."""
    print("\n--- Capturing FastAPI Swagger UI in Google Chrome ---")
    server_process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "careflow.api.app:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=REPO_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    time.sleep(2.5)
    
    # Run Chrome headless to capture the live Swagger page
    chrome_cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1280,820",
        f"--screenshot={output_path}",
        "http://127.0.0.1:8000/docs"
    ]
    subprocess.run(chrome_cmd, check=True)
    print(f"Captured Swagger UI: {output_path} ({os.path.getsize(output_path)} bytes)")
    
    # Kill server process group
    try:
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
    except Exception:
        pass

def capture_github_commits(output_path):
    """Captures real GitHub commits web page from GitHub repository."""
    print("\n--- Capturing GitHub Remote Commits in Google Chrome ---")
    chrome_cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--window-size=1280,800",
        f"--screenshot={output_path}",
        "https://github.com/rofazhasan/CSE3206_CareFlow_System/commits/main"
    ]
    subprocess.run(chrome_cmd, check=True)
    print(f"Captured GitHub commits: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    # 1. Capture Pytest & Coverage in real Terminal
    pytest_img = os.path.join(DOCS_DIR, "screenshot_pytest_test_report.png")
    capture_terminal_command("python3 -m pytest -v --cov=careflow --cov-report=term-missing", pytest_img, cols=115, rows=32, wait_sec=2.5)
    
    # 2. Capture CLI Application Execution in real Terminal
    cli_img = os.path.join(DOCS_DIR, "screenshot_cli_app_output.png")
    capture_terminal_command("python3 -m careflow.cli", cli_img, cols=115, rows=32, wait_sec=2.5)
    
    # 3. Capture Git Log in real Terminal
    term_git_img = os.path.join(DOCS_DIR, "screenshot_terminal_git_log.png")
    capture_terminal_command("git log --graph --oneline --decorate --all -n 14", term_git_img, cols=115, rows=24, wait_sec=1.5)
    
    # 4. Capture GitHub Commits from real browser
    gh_commits_img = os.path.join(DOCS_DIR, "screenshot_github_web_commits.png")
    capture_github_commits(gh_commits_img)
    
    # 5. Capture FastAPI Swagger UI from real browser
    swagger_img = os.path.join(DOCS_DIR, "screenshot_fastapi_swagger_ui.png")
    capture_fastapi_swagger(swagger_img)
    
    # 6. Compose Git Commit Graph Screenshot (combining GitHub web commit history & Terminal git log)
    # This provides undeniable evidence of both remote GitHub commits and local branch DAG with conflict resolution!
    git_final_img = os.path.join(DOCS_DIR, "screenshot_git_commit_graph.png")
    
    # Let's inspect images
    print("\nAll raw real screenshots captured successfully!")
