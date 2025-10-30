"""
Configuration module for Synology Surveillance Station to Telegram bridge

This module centralizes all configuration and constants used by the application.
"""

import os
import sys
import logging

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
LOG_LEVEL = logging.DEBUG


def setup_logger(name):
    """Setup and return a logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
    return logger


# ============================================================================
# ENVIRONMENT VARIABLES - REQUIRED
# ============================================================================

REQUIRED_ENV_VARS = [
    "TG_CHAT_ID",
    "TG_TOKEN",
    "SYNO_IP",
    "SYNO_PORT",
    "SYNO_LOGIN",
    "SYNO_PASS",
]

OPTIONAL_ENV_VARS = {
    "SYNO_OTP": None,  # Two-factor authentication code
    "CONFIG_FILE": "/bot/syno_cam_config.json",  # Camera config cache
    "VIDEO_FILE": "/bot/temp.mp4",  # Temporary video file
    "VIDEO_SEGMENT_DURATION": 10000,  # ms (10 seconds)
    "WEBHOOK_TIMEOUT": 5,  # seconds - wait before fetching video
    "API_TIMEOUT": 30,  # seconds - timeout for API requests
    "GUNICORN_WORKERS": 2,  # Number of worker processes
    "GUNICORN_TIMEOUT": 120,  # seconds
}


# ============================================================================
# TELEGRAM CONFIGURATION
# ============================================================================

TELEGRAM_CHAT_ID = os.environ.get("TG_CHAT_ID")
TELEGRAM_TOKEN = os.environ.get("TG_TOKEN")


# ============================================================================
# SYNOLOGY CONFIGURATION
# ============================================================================

SYNOLOGY_IP = os.environ.get("SYNO_IP")
SYNOLOGY_PORT = os.environ.get("SYNO_PORT", "5000")
SYNOLOGY_LOGIN = os.environ.get("SYNO_LOGIN")
SYNOLOGY_PASSWORD = os.environ.get("SYNO_PASS")
SYNOLOGY_OTP = os.environ.get("SYNO_OTP")
SYNOLOGY_URL = f"http://{SYNOLOGY_IP}:{SYNOLOGY_PORT}/webapi/entry.cgi"

# Synology API endpoints
SYNOLOGY_API = {
    "auth": {
        "api": "SYNO.API.Auth",
        "version": "7",
        "method": "login",
        "session": "SurveillanceStation",
        "format": "cookie12",
    },
    "camera_list": {
        "api": "SYNO.SurveillanceStation.Camera",
        "version": "9",
        "method": "List",
    },
    "recording_list": {
        "api": "SYNO.SurveillanceStation.Recording",
        "version": "6",
        "method": "List",
    },
    "recording_download": {
        "api": "SYNO.SurveillanceStation.Recording",
        "version": "6",
        "method": "Download",
        "playTimeMs": OPTIONAL_ENV_VARS["VIDEO_SEGMENT_DURATION"],
    },
    "camera_status": {
        "api": "SYNO.SurveillanceStation.Camera.Status",
        "version": "1",
        "method": "OneTime",
    },
}


# ============================================================================
# FILE PATHS
# ============================================================================

CONFIG_FILE = os.environ.get("CONFIG_FILE", OPTIONAL_ENV_VARS["CONFIG_FILE"])
VIDEO_FILE = os.environ.get("VIDEO_FILE", OPTIONAL_ENV_VARS["VIDEO_FILE"])


# ============================================================================
# TIMING AND BEHAVIOR
# ============================================================================

VIDEO_SEGMENT_DURATION = int(
    os.environ.get(
        "VIDEO_SEGMENT_DURATION", OPTIONAL_ENV_VARS["VIDEO_SEGMENT_DURATION"]
    )
)  # milliseconds

WEBHOOK_TIMEOUT = int(
    os.environ.get("WEBHOOK_TIMEOUT", OPTIONAL_ENV_VARS["WEBHOOK_TIMEOUT"])
)  # seconds - wait before fetching video

API_TIMEOUT = int(
    os.environ.get("API_TIMEOUT", OPTIONAL_ENV_VARS["API_TIMEOUT"])
)  # seconds - timeout for requests


# ============================================================================
# GUNICORN CONFIGURATION
# ============================================================================

GUNICORN_WORKERS = int(
    os.environ.get("GUNICORN_WORKERS", OPTIONAL_ENV_VARS["GUNICORN_WORKERS"])
)

GUNICORN_TIMEOUT = int(
    os.environ.get("GUNICORN_TIMEOUT", OPTIONAL_ENV_VARS["GUNICORN_TIMEOUT"])
)


# ============================================================================
# DEPENDENCIES - AUTO INSTALL
# ============================================================================

DEPENDENCIES = {
    "telebot": "pyTelegramBotAPI",
    "flask": "flask",
    "requests": "requests",
}
