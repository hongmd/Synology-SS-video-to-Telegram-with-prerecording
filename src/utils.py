"""
Utility functions for Synology Surveillance Station to Telegram bridge

This module contains helper functions used throughout the application.
"""

import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def ensure_module_installed(module_name, package_name=None):
    """Ensure a Python module is installed, installing it if necessary

    Args:
        module_name (str): Name of the module to import (e.g., 'telebot')
        package_name (str): Name of the pip package (e.g., 'pyTelegramBotAPI').
                           If None, uses module_name

    Returns:
        module: The imported module

    Raises:
        SystemExit: If installation fails
    """
    package = package_name or module_name

    try:
        module = __import__(module_name)
        logger.info(f"Module {module_name} is already installed")
        return module
    except ModuleNotFoundError:
        logger.info(f"Module {module_name} is not installed")
        logger.info(f"Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
            )
            logger.info(f"Successfully installed {package}")
            module = __import__(module_name)
            return module
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            sys.exit(1)
