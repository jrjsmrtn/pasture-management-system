# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT
"""
API performance baseline tests for Pasture Management System.

Tests REST API response times to establish baselines and detect regressions.
Target: All API responses should complete in <500ms.
"""

import time

import requests


class APIPerformanceTest:
    """API performance testing for PMS."""

    def __init__(self, base_url: str = "http://localhost:9080/pms"):
        """Initialize API performance test.

        Args:
            base_url: Base URL for PMS instance
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}

    def login(self, username: str = "admin", password: str = "admin") -> bool:
        """Login to PMS to get authenticated session.

        Args:
            username: Login username
            password: Login password

        Returns:
            True if login successful
        """
        try:
            response = self.session.post(
                f"{self.base_url}/",
                data={
                    "__login_name": username,
                    "__login_password": password,
                    "@action": "Login",
                },
                timeout=5,
            )
            return response.status_code == 200 and "logout" in response.text.lower()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Login failed: {e}")
            return False

    def measure_request(self, name: str, method: str, path: str, **kwargs) -> dict:
        """Measure API request response time.

        Args:
            name: Test name for reporting
            method: HTTP method (GET, POST, etc.)
            path: API path (relative to base_url)
            **kwargs: Additional requests arguments

        Returns:
            Test result dictionary
        """
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", 5)

        try:
            start = time.time()
            response = self.session.request(method, url, **kwargs)
            elapsed = time.time() - start

            self.results[name] = {
                "time": elapsed,
                "status_code": response.status_code,
                "passed": elapsed < 0.5 and response.status_code < 400,
                "size_bytes": len(response.content),
            }
        except requests.exceptions.RequestException as e:
            self.results[name] = {
                "time": -1,
                "error": str(e),
                "passed": False,
            }

        return self.results[name]

    def test_homepage(self) -> dict:
        """Test homepage API response time.

        Target: <500ms
        """
        self.measure_request("homepage", "GET", "/")
        return self.results["homepage"]

    def test_issue_list(self) -> dict:
        """Test issue list API response time.

        Target: <500ms
        """
        self.measure_request("issue_list", "GET", "/issue?@template=index")
        return self.results["issue_list"]

    def test_issue_create_form(self) -> dict:
        """Test issue creation form API response time.

        Target: <500ms
        """
        self.measure_request("issue_create_form", "GET", "/issue?@template=item")
        return self.results["issue_create_form"]

    def test_ci_list(self) -> dict:
        """Test CI list API response time.

        Target: <500ms
        """
        self.measure_request("ci_list", "GET", "/ci?@template=index")
        return self.results["ci_list"]

    def test_ci_item_form(self) -> dict:
        """Test CI item form API response time.

        Target: <500ms
        """
        self.measure_request("ci_item_form", "GET", "/ci?@template=item")
        return self.results["ci_item_form"]

    def test_change_list(self) -> dict:
        """Test change request list API response time.

        Target: <500ms
        """
        self.measure_request("change_list", "GET", "/change?@template=index")
        return self.results["change_list"]

    def test_user_list(self) -> dict:
        """Test user list API response time.

        Target: <500ms
        """
        self.measure_request("user_list", "GET", "/user?@template=index")
        return self.results["user_list"]

    def test_search_redirect(self) -> dict:
        """Test search functionality response time.

        Target: <500ms
        """
        self.measure_request(
            "search_redirect",
            "GET",
            "/issue?@search_text=test&@template=search",
            allow_redirects=False,
        )
        return self.results["search_redirect"]

    def run_all_tests(self) -> dict:
        """Run all API performance tests.

        Returns:
            Complete results dictionary
        """
        # Check server is running
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            if response.status_code != 200:
                print(f"⚠️  Server not responding correctly: {response.status_code}")
                print("   Run: ./scripts/reset-test-db.sh admin")
                return {"error": "Server not responding"}
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Server not reachable: {e}")
            print("   Run: ./scripts/reset-test-db.sh admin")
            return {"error": "Server not reachable"}

        # Login first
        if not self.login():
            print("⚠️  Login failed")
            return {"error": "Login failed"}

        tests = [
            ("Homepage", self.test_homepage),
            ("Issue List", self.test_issue_list),
            ("Issue Create Form", self.test_issue_create_form),
            ("CI List", self.test_ci_list),
            ("CI Item Form", self.test_ci_item_form),
            ("Change List", self.test_change_list),
            ("User List", self.test_user_list),
            ("Search Redirect", self.test_search_redirect),
        ]

        print("=" * 60)
        print("API PERFORMANCE BASELINE TESTS")
        print("=" * 60)
        print(f"Server: {self.base_url}")
        print("Target: All responses < 500ms")
        print("=" * 60)

        for name, test_func in tests:
            result = test_func()
            if "error" in result:
                print(f"❌ FAIL {name}: {result['error']}")
            else:
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                size_kb = result["size_bytes"] / 1024
                print(
                    f"{status} {name}: {result['time']:.4f}s "
                    f"({result['status_code']}, {size_kb:.1f}KB)"
                )

        print("=" * 60)

        # Summary
        valid_results = {k: v for k, v in self.results.items() if "error" not in v}
        total_tests = len(valid_results)
        passed_tests = sum(1 for r in valid_results.values() if r["passed"])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Results: {passed_tests}/{total_tests} passed ({pass_rate:.1f}%)")
        print("=" * 60)

        return self.results


if __name__ == "__main__":
    tester = APIPerformanceTest()
    results = tester.run_all_tests()

    # Exit with appropriate code
    if "error" in results:
        exit(1)

    valid_results = {k: v for k, v in results.items() if "error" not in v}
    passed = all(r["passed"] for r in valid_results.values())
    exit(0 if passed else 1)
