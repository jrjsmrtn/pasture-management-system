# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT
"""
Database performance baseline tests for Pasture Management System.

Tests database query performance to establish baselines and detect regressions.
Target: All queries should complete in <1 second.
"""

import sqlite3
import time
from pathlib import Path
from typing import Callable


class DatabasePerformanceTest:
    """Database performance testing for PMS."""

    def __init__(self, db_path: str = "tracker/db/db"):
        """Initialize database performance test.

        Args:
            db_path: Path to Roundup SQLite database
        """
        self.db_path = db_path
        self.results = {}

    def measure_query(self, name: str, query: str, params: tuple = ()) -> float:
        """Measure single query execution time.

        Args:
            name: Test name for reporting
            query: SQL query to execute
            params: Query parameters

        Returns:
            Execution time in seconds
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start = time.time()
        cursor.execute(query, params)
        results = cursor.fetchall()
        elapsed = time.time() - start

        conn.close()

        self.results[name] = {
            "time": elapsed,
            "rows": len(results),
            "passed": elapsed < 1.0,
        }

        return elapsed

    def test_issue_list_query(self) -> dict:
        """Test issue list retrieval performance.

        Target: <1 second for listing all issues
        """
        query = "SELECT * FROM _issue"
        self.measure_query("issue_list", query)
        return self.results["issue_list"]

    def test_issue_search_query(self) -> dict:
        """Test issue search performance.

        Target: <1 second for search with filters
        """
        query = """
        SELECT _issue.* FROM _issue
        WHERE _issue._title LIKE ?
        OR _issue._status IN (
            SELECT id FROM _status WHERE _name = 'open'
        )
        """
        self.measure_query("issue_search", query, ("%bug%",))
        return self.results["issue_search"]

    def test_ci_list_query(self) -> dict:
        """Test CI list retrieval performance.

        Target: <1 second for listing all CIs
        """
        query = "SELECT * FROM _ci"
        self.measure_query("ci_list", query)
        return self.results["ci_list"]

    def test_ci_search_query(self) -> dict:
        """Test CI search with filters performance.

        Target: <1 second for filtered CI search
        """
        query = """
        SELECT _ci.* FROM _ci
        WHERE _ci._name LIKE ?
        OR _ci._type IN (
            SELECT id FROM _citype WHERE _name = 'Server'
        )
        """
        self.measure_query("ci_search", query, ("%server%",))
        return self.results["ci_search"]

    def test_change_request_join_query(self) -> dict:
        """Test change request with join performance.

        Target: <1 second for complex join queries
        """
        query = """
        SELECT cr.*, u._username
        FROM _change AS cr
        LEFT JOIN _user AS u ON cr._creator = u.id
        WHERE cr._status IN (
            SELECT id FROM _changestatus WHERE _name IN ('Open', 'Approved')
        )
        """
        self.measure_query("change_request_join", query)
        return self.results["change_request_join"]

    def test_history_query(self) -> dict:
        """Test history/journal query performance.

        Target: <1 second for audit history retrieval
        """
        query = """
        SELECT * FROM issue__journal
        ORDER BY date DESC
        LIMIT 100
        """
        self.measure_query("history_query", query)
        return self.results["history_query"]

    def test_aggregate_query(self) -> dict:
        """Test aggregate statistics query performance.

        Target: <1 second for dashboard statistics
        """
        query = """
        SELECT
            _status._name AS status,
            COUNT(_issue.id) AS count
        FROM _issue
        LEFT JOIN _status ON _issue._status = _status.id
        GROUP BY _status._name
        """
        self.measure_query("aggregate_query", query)
        return self.results["aggregate_query"]

    def run_all_tests(self) -> dict:
        """Run all database performance tests.

        Returns:
            Complete results dictionary
        """
        # Check database exists
        if not Path(self.db_path).exists():
            print(f"⚠️  Database not found: {self.db_path}")
            print("   Run: ./scripts/reset-test-db.sh admin")
            return {"error": "Database not found"}

        tests = [
            ("Issue List Query", self.test_issue_list_query),
            ("Issue Search Query", self.test_issue_search_query),
            ("CI List Query", self.test_ci_list_query),
            ("CI Search Query", self.test_ci_search_query),
            ("Change Request Join Query", self.test_change_request_join_query),
            ("History Query", self.test_history_query),
            ("Aggregate Query", self.test_aggregate_query),
        ]

        print("=" * 60)
        print("DATABASE PERFORMANCE BASELINE TESTS")
        print("=" * 60)
        print(f"Database: {self.db_path}")
        print("Target: All queries < 1.0 second")
        print("=" * 60)

        for name, test_func in tests:
            result = test_func()
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {name}: {result['time']:.4f}s ({result['rows']} rows)")

        print("=" * 60)

        # Summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["passed"])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Results: {passed_tests}/{total_tests} passed ({pass_rate:.1f}%)")
        print("=" * 60)

        return self.results


if __name__ == "__main__":
    tester = DatabasePerformanceTest()
    results = tester.run_all_tests()

    # Exit with appropriate code
    if "error" in results:
        exit(1)

    passed = all(r["passed"] for r in results.values())
    exit(0 if passed else 1)
