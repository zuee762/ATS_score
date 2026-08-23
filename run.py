"""One-click resilient Launcher for ATS Resume Analyzer & AI Tailor."""

import os
import sys
import socket
import webbrowser
import threading
import time
from pathlib import Path

# Add project root directory to Python module search path
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def find_available_port(preferred_port=8000):
    """Finds an open port starting from preferred_port."""
    for port in [preferred_port, 8001, 8002, 8080, 5000, 5050]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return preferred_port


def open_browser(port):
    """Wait briefly for the server to start, then open the browser."""
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print("\n" + "=" * 60)
    print("  [SUCCESS] ATS Resume Analyzer & AI Tailor is running!")
    print(f"  [URL] Open in browser: {url}")
    print("=" * 60 + "\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Note: Could not automatically open browser ({e}). Please visit {url}")


if __name__ == "__main__":
    try:
        import uvicorn
        from backend.main import app
    except ImportError as e:
        print(f"\n[ERROR] Missing required dependencies: {e}")
        print("Please run: pip install -r requirements.txt\n")
        sys.exit(1)

    port = find_available_port(8000)
    
    # Start browser in background thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    print(f"Starting server on http://127.0.0.1:{port} ...")
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
    except KeyboardInterrupt:
        print("\nServer stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n[SERVER ERROR] {e}")
