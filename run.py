import os
import signal
import subprocess
import sys
import time


def main():
  base_dir = os.path.dirname(os.path.abspath(__file__))
  dot_venv = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
  venv = os.path.join(base_dir, "venv", "Scripts", "python.exe")
  if os.path.exists(dot_venv):
      python_exe = dot_venv
  elif os.path.exists(venv):
      python_exe = venv
  else:
      python_exe = sys.executable

  # 1. Start FastAPI backend (Port 8000)
  backend_cmd = [
      python_exe,
      "-m",
      "uvicorn",
      "main:app",
      "--reload",
      "--port",
      "8000",
  ]
  print("[SYSTEM] Starting FastAPI backend on http://127.0.0.1:8000...")
  backend_proc = subprocess.Popen(backend_cmd)

  # Small buffer to allow FastAPI to bind port 8000
  time.sleep(2)

  # 2. Start Streamlit frontend (Port 8501)
  frontend_cmd = [
      python_exe,
      "-m",
      "streamlit",
      "run",
      "app.py",
      "--server.port",
      "8501",
  ]
  print("[SYSTEM] Starting Streamlit frontend on http://localhost:8501...")
  frontend_proc = subprocess.Popen(frontend_cmd)

  try:
    # Keep the orchestrator alive while sub-processes run
    while True:
      time.sleep(1)
      if (
          backend_proc.poll() is not None
          or frontend_proc.poll() is not None
      ):
        break
  except KeyboardInterrupt:
    print("\n[SYSTEM] Shutting down services...")
  finally:
    for proc in [backend_proc, frontend_proc]:
      if proc.poll() is None:
        proc.terminate()
        try:
          proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
          proc.kill()
    print("[SYSTEM] All services terminated successfully.")


if __name__ == "__main__":
  main()  
