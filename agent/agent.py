#!/usr/bin/env python3
"""
Cyber Essentials Agent - Fleet Management Agent

This agent wraps the existing scanner and provides:
- Registration with controller
- Periodic heartbeat
- Command polling and execution
- Automatic scan scheduling
- Report upload
"""
import os
import sys
import json
import time
import logging
import platform
import socket
import argparse
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path to import scanner
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import schedule

# Import configuration
from config import (
    CONTROLLER_URL, VERIFY_SSL, HEARTBEAT_INTERVAL, 
    COMMAND_POLL_INTERVAL, SCAN_SCHEDULE, LOG_LEVEL, LOG_FILE
)

# Import token storage utilities
from token_store import store_token, get_token, clear_token

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CEAgent:
    """Cyber Essentials Fleet Agent"""
    
    def __init__(self, controller_url: str = CONTROLLER_URL, verify_ssl: bool = VERIFY_SSL):
        self.controller_url = controller_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.agent_id: Optional[str] = None
        self.agent_token: Optional[str] = None
        self.running = False
        
        logger.info(f"Initializing CE Agent (Controller: {self.controller_url})")
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.agent_token:
            headers["Authorization"] = f"Bearer {self.agent_token}"
        return headers
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_version": platform.version(),
            "ip": self.get_local_ip(),
            "metadata": {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        }
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Create a socket connection to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "unknown"
    
    def register(self) -> bool:
        """Register agent with controller"""
        try:
            logger.info("Attempting to register with controller...")
            
            system_info = self.get_system_info()
            response = requests.post(
                f"{self.controller_url}/api/agents/register",
                json=system_info,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.agent_id = data["agent_id"]
                self.agent_token = data["agent_token"]
                
                # Store token securely
                store_token(self.agent_token)
                
                logger.info(f"Successfully registered as agent {self.agent_id}")
                return True
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False
    
    def load_stored_credentials(self) -> bool:
        """Load stored agent credentials"""
        try:
            token = get_token()
            if token:
                self.agent_token = token
                # TODO: Extract agent_id from token or store separately
                logger.info("Loaded stored credentials")
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to load stored credentials: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to controller"""
        if not self.agent_id or not self.agent_token:
            logger.warning("Cannot send heartbeat: not registered")
            return False
        
        try:
            response = requests.post(
                f"{self.controller_url}/api/agents/{self.agent_id}/heartbeat",
                json={"status": "online"},
                headers=self.get_headers(),
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug("Heartbeat sent successfully")
                return True
            else:
                logger.warning(f"Heartbeat failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            return False
    
    def poll_commands(self):
        """Poll for pending commands"""
        if not self.agent_id or not self.agent_token:
            logger.debug("Cannot poll commands: not registered")
            return
        
        try:
            response = requests.get(
                f"{self.controller_url}/api/agents/{self.agent_id}/commands",
                headers=self.get_headers(),
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                commands = response.json()
                for command in commands:
                    self.execute_command(command)
            elif response.status_code != 404:
                logger.warning(f"Command polling failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Command polling error: {e}")
    
    def execute_command(self, command: Dict[str, Any]):
        """Execute a command"""
        command_id = command["id"]
        command_type = command["command_type"]
        payload = command.get("payload", {})
        
        logger.info(f"Executing command {command_id}: {command_type}")
        
        try:
            if command_type == "scan":
                result = self.run_scan(payload)
                self.submit_command_result(command_id, "completed", result)
            else:
                logger.warning(f"Unknown command type: {command_type}")
                self.submit_command_result(command_id, "failed", {"error": "Unknown command type"})
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            self.submit_command_result(command_id, "failed", {"error": str(e)})
    
    def submit_command_result(self, command_id: str, status: str, result: Dict[str, Any]):
        """Submit command execution result"""
        try:
            response = requests.post(
                f"{self.controller_url}/api/agents/{self.agent_id}/command/{command_id}/result",
                json={"status": status, "result": result},
                headers=self.get_headers(),
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Command result submitted: {command_id}")
            else:
                logger.warning(f"Failed to submit command result: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error submitting command result: {e}")
    
    def run_scan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run the scanner and return results"""
        logger.info("Starting compliance scan...")
        
        # Determine scan mode
        mode = params.get("mode", "standard")
        strict_mode = mode == "strict"
        
        # Import scanner modules
        from scanner.main import main as scanner_main
        from scanner.models import Report, OSInfo
        from scanner.utils import get_os_info
        from scanner import checks
        from scanner.os import windows as osw, macos as osm, linux as osl
        
        # Run all checks
        try:
            results = []
            check_modules = [
                ("Firewalls", checks.firewall),
                ("Secure Configuration", checks.secure_configuration),
                ("Access Control", checks.access_control),
                ("Malware Protection", checks.malware_protection),
                ("Patch Management", checks.patch_management),
                ("Remote Work & MDM", checks.remote_work_mdm)
            ]
            
            for check_name, check_module in check_modules:
                logger.debug(f"Running check: {check_name}")
                res = check_module.run(osw, osm, osl, strict_mode=strict_mode)
                results.append(res)
            
            # Calculate overall status and score
            from scanner.models import combine_statuses, average_score
            overall_status = combine_statuses([r.status for r in results])
            overall_score = average_score([r.score for r in results])
            
            # Build report
            report = {
                "scanner_version": "0.2.0",
                "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "compliance_mode": mode,
                "os": {
                    "platform": platform.system(),
                    "version": platform.version()
                },
                "controls": [r.__dict__ for r in results],
                "overall": {
                    "status": overall_status,
                    "score": overall_score
                }
            }
            
            # Upload report
            self.upload_report(report)
            
            logger.info(f"Scan completed: {overall_status} (score: {overall_score})")
            return {"status": "success", "overall": overall_status, "score": overall_score}
            
        except Exception as e:
            logger.error(f"Scan error: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def upload_report(self, report: Dict[str, Any]):
        """Upload scan report to controller"""
        try:
            response = requests.post(
                f"{self.controller_url}/api/agents/{self.agent_id}/report",
                json={
                    "mode": report.get("compliance_mode", "standard"),
                    "overall_status": report["overall"]["status"],
                    "overall_score": report["overall"]["score"],
                    "payload": report
                },
                headers=self.get_headers(),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Report uploaded successfully: {data.get('report_id')}")
            else:
                logger.warning(f"Report upload failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Report upload error: {e}")
    
    def scheduled_scan(self):
        """Scheduled scan task"""
        logger.info("Running scheduled scan...")
        self.run_scan({"mode": "standard"})
    
    def start_daemon(self):
        """Start agent in daemon mode"""
        logger.info("Starting CE Agent in daemon mode...")
        
        # Try to load stored credentials
        if not self.load_stored_credentials():
            # Register if no stored credentials
            if not self.register():
                logger.error("Failed to register with controller")
                return
        
        # Set up scheduled tasks
        schedule.every(HEARTBEAT_INTERVAL).seconds.do(self.send_heartbeat)
        schedule.every(COMMAND_POLL_INTERVAL).seconds.do(self.poll_commands)
        
        # Set up scan schedule
        if SCAN_SCHEDULE == "daily":
            schedule.every().day.at("02:00").do(self.scheduled_scan)
        elif SCAN_SCHEDULE == "weekly":
            schedule.every().monday.at("02:00").do(self.scheduled_scan)
        
        # Send initial heartbeat
        self.send_heartbeat()
        
        # Main loop
        self.running = True
        logger.info("Agent daemon started successfully")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down agent...")
            self.running = False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Cyber Essentials Fleet Agent")
    parser.add_argument("--controller", type=str, help="Controller URL")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--register", action="store_true", help="Register with controller")
    parser.add_argument("--scan", action="store_true", help="Run one-shot scan")
    parser.add_argument("--mode", choices=["standard", "strict"], default="standard", help="Scan mode")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL verification")
    args = parser.parse_args()
    
    # Set controller URL
    controller_url = args.controller if args.controller else CONTROLLER_URL
    verify_ssl = not args.no_verify_ssl
    
    # Create agent
    agent = CEAgent(controller_url, verify_ssl)
    
    if args.register:
        # Manual registration
        if agent.register():
            print(f"Successfully registered as agent {agent.agent_id}")
            print(f"Token stored securely")
        else:
            print("Registration failed")
            sys.exit(1)
    
    elif args.scan:
        # One-shot scan
        if not agent.load_stored_credentials():
            print("Not registered. Run with --register first.")
            sys.exit(1)
        
        result = agent.run_scan({"mode": args.mode})
        print(f"Scan completed: {result}")
    
    elif args.daemon:
        # Daemon mode
        agent.start_daemon()
    
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
