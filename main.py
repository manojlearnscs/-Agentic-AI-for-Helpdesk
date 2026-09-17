import sys
import os
import subprocess

def print_banner():
    print("""
    ===============================================================
       AI IT HELPDESK AGENT  (Use Case #4: Agent + RAG + Tools)
    ===============================================================
    """)

def main():
    print_banner()
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from cli import main as cli_main
        cli_main()
    else:
        print("Launching Streamlit Web Application interface on http://localhost:8501 ...")
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nApplication stopped.")

if __name__ == "__main__":
    main()
