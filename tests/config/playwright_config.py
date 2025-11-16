# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Playwright configuration for PMS BDD testing.

This module provides Playwright browser configuration for consistent
testing across web UI scenarios. All screenshots are captured at 1024x768
resolution with English locale.
"""

from typing import Any


# Viewport configuration for consistent screenshots
VIEWPORT = {
    "width": 1024,
    "height": 768,
}

# Browser configuration
BROWSER_CONFIG: dict[str, Any] = {
    "headless": True,  # Run headless in CI, can override for debugging
    "slow_mo": 0,  # Milliseconds to slow down operations (useful for debugging)
}

# Context configuration
CONTEXT_CONFIG: dict[str, Any] = {
    "viewport": VIEWPORT,
    "locale": "en-US",  # English locale
    "timezone_id": "America/New_York",
    "ignore_https_errors": True,  # For local development with self-signed certs
    "record_video_dir": None,  # Can be set to enable video recording
    "record_har_path": None,  # Can be set to record network traffic
}

# Screenshot configuration
SCREENSHOT_CONFIG: dict[str, Any] = {
    "path": None,  # Set dynamically in environment.py
    "full_page": False,  # Capture viewport only for consistent sizing
    "type": "png",
}

# Default timeouts (milliseconds)
TIMEOUTS = {
    "default": 30000,  # 30 seconds default timeout
    "navigation": 30000,  # Page navigation timeout
    "action": 10000,  # Action timeout (click, fill, etc.)
}

# Base URL for the tracker
# Override with TRACKER_URL environment variable
# Using port 9080 to avoid conflicts with other services (e.g., Docker/Podman on 8080)
DEFAULT_TRACKER_URL = "http://localhost:9080/pms/"


def get_browser_args() -> list[str]:
    """
    Get browser launch arguments.

    Returns:
        List of browser arguments
    """
    return [
        "--disable-blink-features=AutomationControlled",  # Avoid detection
        "--disable-dev-shm-usage",  # Overcome limited resource problems
        "--no-sandbox",  # Required for running in some CI environments
    ]


def get_launch_options(headless: bool = True) -> dict[str, Any]:
    """
    Get complete browser launch options.

    Args:
        headless: Whether to run in headless mode

    Returns:
        Browser launch options dictionary
    """
    return {
        **BROWSER_CONFIG,
        "headless": headless,
        "args": get_browser_args(),
    }


def get_context_options() -> dict[str, Any]:
    """
    Get browser context options.

    Returns:
        Browser context options dictionary
    """
    return CONTEXT_CONFIG.copy()
