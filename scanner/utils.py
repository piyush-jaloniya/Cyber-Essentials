import platform
import subprocess
import logging
from typing import Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)

def run_cmd(cmd: str, shell: bool = True, timeout: int = 15) -> Tuple[int, str, str]:
    """
    Execute a shell command and return (return_code, stdout, stderr).
    Logs errors for debugging.
    """
    try:
        logger.debug(f"Executing command: {cmd}")
        proc = subprocess.run(cmd, shell=shell, capture_output=True, timeout=timeout, text=True)
        if proc.returncode != 0:
            # Only log at DEBUG level (not WARNING) to avoid cluttering console when checks probe for optional features
            logger.debug(f"Command returned non-zero exit code {proc.returncode}: {cmd}")
            if proc.stderr:
                logger.debug(f"stderr: {proc.stderr.strip()}")
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s: {cmd}")
        return 1, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Command execution failed: {cmd} - Error: {str(e)}")
        return 1, "", str(e)

def get_os_info():
    """
    Detect operating system and version.
    Returns tuple of (os_name, version).
    """
    system = platform.system()
    if system == "Windows":
        # Get actual Windows version name (Windows 10/11)
        try:
            code, out, _ = run_cmd('wmic os get Caption /value')
            if code == 0 and "Caption=" in out:
                caption = out.split("Caption=")[1].strip().split('\n')[0].strip()
                version = platform.version()
                logger.info(f"Detected OS: {caption} (version {version})")
                return caption, version
        except Exception as e:
            logger.warning(f"Failed to get detailed Windows version: {e}")
        fallback = ("Windows", platform.version())
        logger.info(f"Using fallback OS detection: {fallback[0]} {fallback[1]}")
        return fallback
    elif system == "Darwin":
        os_info = ("macOS", platform.mac_ver()[0])
        logger.info(f"Detected OS: {os_info[0]} {os_info[1]}")
        return os_info
    else:
        os_info = ("Linux", platform.release())
        logger.info(f"Detected OS: {os_info[0]} {os_info[1]}")
        return os_info