# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT
"""
UI performance baseline tests for Pasture Management System.

Tests web UI page load times using Playwright to establish baselines.
Target: All page loads should complete in <2 seconds.
"""

import time
from typing import Optional

from playwright.sync_api import Browser, Page, sync_playwright


class UIPerformanceTest:
    """UI performance testing for PMS using Playwright."""

    def __init__(self, base_url: str = "http://localhost:9080/pms"):
        """Initialize UI performance test.

        Args:
            base_url: Base URL for PMS instance
        """
        self.base_url = base_url
        self.results = {}
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def setup(self):
        """Set up Playwright browser and page."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()

    def teardown(self):
        """Clean up Playwright resources."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, "playwright"):
            self.playwright.stop()

    def login(self, username: str = "admin", password: str = "admin") -> bool:
        """Login to PMS to get authenticated session.

        Args:
            username: Login username
            password: Login password

        Returns:
            True if login successful
        """
        try:
            self.page.goto(f"{self.base_url}/")
            self.page.fill('input[name="__login_name"]', username)
            self.page.fill('input[name="__login_password"]', password)
            # Click the Login button specifically (not the search submit button)
            self.page.click('input[type="submit"][value="Login"]')
            self.page.wait_for_load_state("networkidle", timeout=5000)
            return "logout" in self.page.content().lower()
        except Exception as e:
            print(f"⚠️  Login failed: {e}")
            return False

    def measure_page_load(
        self, name: str, path: str, wait_for_selector: Optional[str] = None
    ) -> dict:
        """Measure page load time.

        Args:
            name: Test name for reporting
            path: Page path (relative to base_url)
            wait_for_selector: Optional selector to wait for

        Returns:
            Test result dictionary
        """
        url = f"{self.base_url}{path}"

        try:
            start = time.time()
            self.page.goto(url, wait_until="networkidle", timeout=5000)

            # Wait for specific element if provided
            if wait_for_selector:
                self.page.wait_for_selector(wait_for_selector, timeout=2000)

            elapsed = time.time() - start

            # Get performance metrics
            performance = self.page.evaluate(
                """() => {
                const timing = performance.timing;
                return {
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    loadComplete: timing.loadEventEnd - timing.navigationStart,
                    domInteractive: timing.domInteractive - timing.navigationStart
                };
            }"""
            )

            self.results[name] = {
                "time": elapsed,
                "passed": elapsed < 2.0,
                "dom_content_loaded_ms": performance.get("domContentLoaded", 0),
                "load_complete_ms": performance.get("loadComplete", 0),
                "dom_interactive_ms": performance.get("domInteractive", 0),
            }
        except Exception as e:
            self.results[name] = {
                "time": -1,
                "error": str(e),
                "passed": False,
            }

        return self.results[name]

    def test_homepage_load(self) -> dict:
        """Test homepage load time.

        Target: <2 seconds
        """
        self.measure_page_load("homepage_load", "/")
        return self.results["homepage_load"]

    def test_issue_list_load(self) -> dict:
        """Test issue list page load time.

        Target: <2 seconds
        """
        self.measure_page_load(
            "issue_list_load", "/issue?@template=index", wait_for_selector="table.list"
        )
        return self.results["issue_list_load"]

    def test_issue_create_form_load(self) -> dict:
        """Test issue create form load time.

        Target: <2 seconds
        """
        self.measure_page_load(
            "issue_create_form_load", "/issue?@template=item", wait_for_selector="form"
        )
        return self.results["issue_create_form_load"]

    def test_ci_list_load(self) -> dict:
        """Test CI list page load time.

        Target: <2 seconds
        """
        # Don't wait for table.list - may not exist if no CIs
        self.measure_page_load("ci_list_load", "/ci?@template=index")
        return self.results["ci_list_load"]

    def test_ci_item_form_load(self) -> dict:
        """Test CI item form page load time.

        Target: <2 seconds
        """
        self.measure_page_load("ci_item_form_load", "/ci?@template=item", wait_for_selector="form")
        return self.results["ci_item_form_load"]

    def test_change_list_load(self) -> dict:
        """Test change request list page load time.

        Target: <2 seconds
        """
        # Don't wait for table.list - may not exist if no changes
        self.measure_page_load("change_list_load", "/change?@template=index")
        return self.results["change_list_load"]

    def test_user_list_load(self) -> dict:
        """Test user list page load time.

        Target: <2 seconds
        """
        self.measure_page_load("user_list_load", "/user?@template=index", wait_for_selector="table")
        return self.results["user_list_load"]

    def test_search_page_load(self) -> dict:
        """Test search page load time.

        Target: <2 seconds
        """
        self.measure_page_load("search_page_load", "/issue?@template=search")
        return self.results["search_page_load"]

    def run_all_tests(self) -> dict:
        """Run all UI performance tests.

        Returns:
            Complete results dictionary
        """
        try:
            self.setup()

            # Check server is running and login
            if not self.login():
                print("⚠️  Server not reachable or login failed")
                print("   Run: ./scripts/reset-test-db.sh admin")
                return {"error": "Server not reachable or login failed"}

            tests = [
                ("Homepage Load", self.test_homepage_load),
                ("Issue List Load", self.test_issue_list_load),
                ("Issue Create Form Load", self.test_issue_create_form_load),
                ("CI List Load", self.test_ci_list_load),
                ("CI Item Form Load", self.test_ci_item_form_load),
                ("Change List Load", self.test_change_list_load),
                ("User List Load", self.test_user_list_load),
                ("Search Page Load", self.test_search_page_load),
            ]

            print("=" * 60)
            print("UI PERFORMANCE BASELINE TESTS")
            print("=" * 60)
            print(f"Server: {self.base_url}")
            print("Browser: Chromium (headless)")
            print("Target: All pages < 2s")
            print("=" * 60)

            for name, test_func in tests:
                result = test_func()
                if "error" in result:
                    print(f"❌ FAIL {name}: {result['error']}")
                else:
                    status = "✅ PASS" if result["passed"] else "❌ FAIL"
                    dom_ms = result.get("dom_interactive_ms", 0)
                    print(f"{status} {name}: {result['time']:.4f}s (DOM: {dom_ms}ms)")

            print("=" * 60)

            # Summary
            valid_results = {k: v for k, v in self.results.items() if "error" not in v}
            total_tests = len(valid_results)
            passed_tests = sum(1 for r in valid_results.values() if r["passed"])
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            print(f"Results: {passed_tests}/{total_tests} passed ({pass_rate:.1f}%)")
            print("=" * 60)

            return self.results

        finally:
            self.teardown()


if __name__ == "__main__":
    tester = UIPerformanceTest()
    results = tester.run_all_tests()

    # Exit with appropriate code
    if "error" in results:
        exit(1)

    valid_results = {k: v for k, v in results.items() if "error" not in v}
    passed = all(r["passed"] for r in valid_results.values())
    exit(0 if passed else 1)
