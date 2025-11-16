# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Behave environment configuration for PMS BDD testing.

This module sets up the testing environment for Behave scenarios,
including Playwright browser setup, screenshot capture, and database cleanup.
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from behave import fixture, use_fixture
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from tests.config.playwright_config import (
    DEFAULT_TRACKER_URL,
    get_context_options,
    get_launch_options,
)


# Screenshot directory
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


@fixture
def playwright_browser(context):
    """
    Set up Playwright browser for the test run.

    This fixture initializes Playwright and launches a Chromium browser
    that will be shared across scenarios.
    """
    # Start Playwright
    context.playwright = sync_playwright().start()

    # Determine headless mode from environment
    headless = os.getenv("HEADLESS", "true").lower() == "true"

    # Launch browser
    context.browser = context.playwright.chromium.launch(**get_launch_options(headless=headless))

    yield context.browser

    # Cleanup
    context.browser.close()
    context.playwright.stop()


@fixture
def browser_context(context):
    """
    Set up browser context for each scenario.

    This fixture creates a new browser context with configured viewport,
    locale, and other settings for each scenario.
    """
    # Get tracker URL from environment
    tracker_url = os.getenv("TRACKER_URL", DEFAULT_TRACKER_URL)
    context.tracker_url = tracker_url

    # Create new context
    context.context = context.browser.new_context(**get_context_options())

    # Create new page
    context.page = context.context.new_page()

    yield context.context

    # Cleanup
    context.page.close()
    context.context.close()


def before_all(context):
    """
    Run before all tests.

    Set up the Playwright browser instance that will be reused
    across all scenarios for better performance.
    """
    use_fixture(playwright_browser, context)

    # Set up reporting directory
    context.report_dir = Path("reports")
    context.report_dir.mkdir(exist_ok=True)


def before_scenario(context, scenario):
    """
    Run before each scenario.

    Set up a fresh browser context for each scenario to ensure isolation.
    Only set up browser for web-ui scenarios.
    """
    # Only set up browser for web UI scenarios (check tags)
    # API and CLI scenarios don't need browser
    has_web_ui_tag = "web-ui" in scenario.effective_tags
    has_api_tag = "api" in scenario.effective_tags
    has_cli_tag = "cli" in scenario.effective_tags

    is_web_ui = has_web_ui_tag and not (has_api_tag or has_cli_tag)

    if is_web_ui:
        use_fixture(browser_context, context)
    else:
        # CLI or API scenario - just set tracker URL and directory
        context.tracker_url = os.getenv("TRACKER_URL", DEFAULT_TRACKER_URL)
        context.tracker_dir = "tracker"
        context.page = None  # Explicitly set to None

    # Store scenario name for screenshot naming
    context.scenario_name = scenario.name.replace(" ", "_").lower()


def after_step(context, step):
    """
    Run after each step.

    Capture screenshots on step failure for debugging.
    """
    if step.status == "failed":
        # Generate screenshot filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_name = context.scenario_name
        step_name = step.name.replace(" ", "_").lower()[:50]
        screenshot_name = f"{scenario_name}_{step_name}_{timestamp}_FAILED.png"
        screenshot_path = SCREENSHOT_DIR / screenshot_name

        # Capture screenshot
        try:
            context.page.screenshot(
                path=str(screenshot_path),
                full_page=False,  # Capture viewport only (1024x768)
            )
            print(f"\nScreenshot saved: {screenshot_path}")

            # Attach screenshot to report if using pytest-html or similar
            if hasattr(context, "embed"):
                with open(screenshot_path, "rb") as screenshot_file:
                    context.embed(
                        "image/png",
                        screenshot_file.read(),
                        caption=f"Failed: {step.name}",
                    )
        except Exception as e:
            print(f"\nFailed to capture screenshot: {e}")


def _reinitialize_database(context):
    """
    Reinitialize the tracker database to ensure test isolation.

    This deletes the database and recreates it from initial_data.py,
    providing a clean state for each scenario.
    """
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    cleanup_enabled = os.getenv("CLEANUP_TEST_DATA", "true").lower() == "true"

    if not cleanup_enabled:
        return

    try:
        # Delete database files
        db_dir = Path(tracker_dir) / "db"
        if db_dir.exists():
            shutil.rmtree(db_dir)

        # Reinitialize database
        # Provide admin password twice for confirmation
        cmd = ["roundup-admin", "-i", tracker_dir, "initialise"]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input="admin\nadmin\n", timeout=30)

        if process.returncode != 0:
            print(f"\nWarning: Database reinit failed: {stderr}")

    except Exception as e:
        # Don't fail the test if cleanup fails
        print(f"\nWarning: Failed to reinitialize database: {e}")


def after_scenario(context, scenario):
    """
    Run after each scenario.

    Capture final screenshot for passed scenarios (optional)
    and reinitialize database for test isolation.
    """
    # Reinitialize database to clean state
    _reinitialize_database(context)

    # Optionally capture screenshot for passed scenarios
    if scenario.status == "passed" and os.getenv("SCREENSHOT_ON_PASS", "false").lower() == "true":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"{context.scenario_name}_{timestamp}_PASSED.png"
        screenshot_path = SCREENSHOT_DIR / screenshot_name

        try:
            context.page.screenshot(
                path=str(screenshot_path),
                full_page=False,
            )
            print(f"\nScreenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"\nFailed to capture screenshot: {e}")


def after_all(context):
    """
    Run after all tests.

    Final cleanup and reporting.
    """
    # Additional cleanup if needed
    pass
