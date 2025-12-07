"""Agent configuration"""
import os
from typing import Optional

# Controller settings
CONTROLLER_URL = os.getenv("CE_CONTROLLER_URL", "https://controller.local:8000")
VERIFY_SSL = os.getenv("CE_VERIFY_SSL", "true").lower() == "true"

# Agent settings
HEARTBEAT_INTERVAL = int(os.getenv("CE_HEARTBEAT_INTERVAL", "60"))  # seconds
COMMAND_POLL_INTERVAL = int(os.getenv("CE_COMMAND_POLL_INTERVAL", "30"))  # seconds
SCAN_SCHEDULE = os.getenv("CE_SCAN_SCHEDULE", "daily")  # daily, weekly, manual

# Security
TOKEN_STORE_NAME = "ce-agent-token"
TOKEN_STORE_USERNAME = "ce-agent"

# Logging
LOG_LEVEL = os.getenv("CE_LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("CE_LOG_FILE", "ce-agent.log")
