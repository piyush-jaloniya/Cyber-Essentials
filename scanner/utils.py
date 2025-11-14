import platform
import subprocess
from typing import Tuple, Optional

def run_cmd(cmd: str, shell: bool = True, timeout: int = 15) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, shell=shell, capture_output=True, timeout=timeout, text=True)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def get_os_info():
    system = platform.system()
    if system == "Windows":
           # Get actual Windows version name (Windows 10/11)
           try:
               code, out, _ = run_cmd('wmic os get Caption /value')
               if code == 0 and "Caption=" in out:
                   caption = out.split("Caption=")[1].strip().split('\n')[0].strip()
                   version = platform.version()
                   return caption, version
           except Exception:
               pass
           return "Windows", platform.version()
    elif system == "Darwin":
        return "macOS", platform.mac_ver()[0]
    else:
        return "Linux", platform.release()