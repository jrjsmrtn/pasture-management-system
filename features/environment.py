# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Behave environment configuration for PMS BDD testing.

This module sets up the testing environment for Behave scenarios,
including Playwright browser setup, screenshot capture, and cleanup.
"""

import os
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


def _cleanup_test_data(context):
    """
    Clean up test issues and changes created during the scenario.

    This function deletes issues and changes created during testing to prevent
    database bloat and ensure test isolation.
    """
    # Get tracker directory
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    cleanup_enabled = os.getenv("CLEANUP_TEST_DATA", "true").lower() == "true"
    if not cleanup_enabled:
        return

    # Clean up issues
    issue_ids = set()

    # From single issue creation
    if hasattr(context, "created_issue_id"):
        issue_id = context.created_issue_id
        # Extract numeric ID
        if issue_id.startswith("issue"):
            issue_id = issue_id[5:]
        issue_ids.add(issue_id)

    # From multiple issue creation
    if hasattr(context, "test_issue_ids"):
        issue_ids.update(context.test_issue_ids)

    # From API creation
    if hasattr(context, "api_issue_id"):
        issue_ids.add(context.api_issue_id)

    # Delete each issue
    if issue_ids:
        for issue_id in issue_ids:
            try:
                cmd = ["roundup-admin", "-i", tracker_dir, "retire", f"issue{issue_id}"]
                subprocess.run(cmd, capture_output=True, timeout=10, check=False)
            except Exception as e:
                # Don't fail the test if cleanup fails
                print(f"\nWarning: Failed to cleanup issue{issue_id}: {e}")

    # Clean up changes
    change_ids = set()

    # From single change creation
    if hasattr(context, "created_change_id"):
        change_id = context.created_change_id
        # Extract numeric ID
        if change_id.startswith("change"):
            change_id = change_id[6:]
        change_ids.add(change_id)

    # From multiple change creation
    if hasattr(context, "test_change_ids"):
        change_ids.update(context.test_change_ids)

    # From API creation
    if hasattr(context, "api_change_id"):
        change_ids.add(context.api_change_id)

    # From change list scenarios
    if hasattr(context, "change_ids"):
        change_ids.update(context.change_ids)

    # Delete each change
    if change_ids:
        for change_id in change_ids:
            try:
                cmd = ["roundup-admin", "-i", tracker_dir, "retire", f"change{change_id}"]
                subprocess.run(cmd, capture_output=True, timeout=10, check=False)
            except Exception as e:
                # Don't fail the test if cleanup fails
                print(f"\nWarning: Failed to cleanup change{change_id}: {e}")


def after_scenario(context, scenario):
    """
    Run after each scenario.

    Capture final screenshot for passed scenarios (optional)
    and perform cleanup of test data.
    """
    # Clean up test data (issues and changes)
    _cleanup_test_data(context)

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
