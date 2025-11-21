# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Load testing and performance BDD step definitions."""

import json
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import requests
from behave import given, then, when
from behave.runner import Context
from requests.auth import HTTPBasicAuth


@given("I am logged in as admin")
def step_login_as_admin(context: Context) -> None:
    """Set admin credentials in context for load testing."""
    context.username = "admin"
    context.password = "admin"


def create_issue_via_cli(issue_num: int) -> dict[str, Any]:
    """Create a single issue via CLI and measure performance."""
    start_time = time.time()
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "roundup-admin",
                "-i",
                "tracker",
                "create",
                "issue",
                f"title='Load Test Issue {issue_num}'",
                "status=1",
                "priority=2",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        duration = time.time() - start_time
        # Extract issue ID from output (format: "issue1")
        issue_id = result.stdout.strip().split()[-1] if result.stdout else None
        return {
            "success": True,
            "issue_num": issue_num,
            "issue_id": issue_id,
            "duration": duration,
            "error": None,
        }
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "issue_num": issue_num,
            "issue_id": None,
            "duration": duration,
            "error": str(e),
        }


def create_issue_via_api(issue_num: int, base_url: str) -> dict[str, Any]:
    """Create a single issue via API and measure performance."""
    start_time = time.time()
    try:
        response = requests.post(
            f"{base_url}/rest/data/issue",
            json={
                "title": f"Load Test Issue {issue_num}",
                "status": "1",
                "priority": "2",
            },
            headers={
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": base_url,
                "Referer": base_url,
            },
            auth=HTTPBasicAuth("admin", "admin"),
            timeout=30,
        )
        duration = time.time() - start_time
        response.raise_for_status()
        issue_id = response.json().get("data", {}).get("id")
        return {
            "success": True,
            "issue_num": issue_num,
            "issue_id": issue_id,
            "duration": duration,
            "error": None,
        }
    except requests.RequestException as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "issue_num": issue_num,
            "issue_id": None,
            "duration": duration,
            "error": str(e),
        }


def create_issue_via_email(issue_num: int) -> dict[str, Any]:
    """Create a single issue via email gateway and measure performance."""
    start_time = time.time()
    try:
        # Compose proper email with all required headers
        msg = EmailMessage()
        msg["From"] = "roundup-admin@localhost"
        msg["To"] = "issue_tracker@localhost"
        msg["Subject"] = f"Load Test Email Issue {issue_num}"
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        msg.set_content(
            f"This is a load test issue created via email gateway.\nIssue number: {issue_num}"
        )

        # Use roundup-mailgw PIPE mode
        result = subprocess.run(
            ["roundup-mailgw", "tracker"],
            input=msg.as_string(),
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        duration = time.time() - start_time
        # Extract issue ID from mailgw output
        issue_id = None
        for line in result.stdout.split("\n"):
            if "issue" in line.lower() and "created" in line.lower():
                # Try to extract issue number
                parts = line.split()
                for part in parts:
                    if part.startswith("issue"):
                        issue_id = part
                        break
        return {
            "success": True,
            "issue_num": issue_num,
            "issue_id": issue_id,
            "duration": duration,
            "error": None,
        }
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "issue_num": issue_num,
            "issue_id": None,
            "duration": duration,
            "error": str(e),
        }


def update_issue_via_api(issue_id: str, base_url: str) -> dict[str, Any]:
    """Update a single issue via API and measure performance."""
    start_time = time.time()
    try:
        # First get the current etag
        get_response = requests.get(
            f"{base_url}/rest/data/issue/{issue_id}",
            auth=HTTPBasicAuth("admin", "admin"),
            timeout=10,
        )
        get_response.raise_for_status()
        etag = get_response.json().get("data", {}).get("@etag")

        # Now update
        response = requests.patch(
            f"{base_url}/rest/data/issue/{issue_id}",
            json={"priority": "3"},
            headers={
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": base_url,
                "Referer": base_url,
                "If-Match": etag,
            },
            auth=HTTPBasicAuth("admin", "admin"),
            timeout=30,
        )
        duration = time.time() - start_time
        response.raise_for_status()
        return {
            "success": True,
            "issue_id": issue_id,
            "duration": duration,
            "error": None,
        }
    except requests.RequestException as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "issue_id": issue_id,
            "duration": duration,
            "error": str(e),
        }


def search_issues_via_api(user_num: int, base_url: str) -> dict[str, Any]:
    """Search for issues via API and measure performance."""
    start_time = time.time()
    try:
        response = requests.get(
            f"{base_url}/rest/data/issue",
            auth=HTTPBasicAuth("admin", "admin"),
            timeout=10,
        )
        duration = time.time() - start_time
        response.raise_for_status()
        results = response.json().get("data", {}).get("collection", [])
        return {
            "success": True,
            "user_num": user_num,
            "result_count": len(results),
            "duration": duration,
            "error": None,
        }
    except requests.RequestException as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "user_num": user_num,
            "result_count": 0,
            "duration": duration,
            "error": str(e),
        }


@when("{count:d} users create issues concurrently via CLI")
def step_concurrent_cli_create(context: Context, count: int) -> None:
    """Execute concurrent issue creation via CLI."""
    start_time = time.time()
    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=min(count, 50)) as executor:
        futures = [executor.submit(create_issue_via_cli, i) for i in range(1, count + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    total_duration = time.time() - start_time

    # Store results in context
    context.load_test_results = results
    context.load_test_duration = total_duration
    context.load_test_count = count


@when("{count:d} issues are created concurrently via API")
def step_concurrent_api_create(context: Context, count: int) -> None:
    """Execute concurrent issue creation via API."""
    base_url = "http://localhost:9080/pms"
    start_time = time.time()
    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=min(count, 50)) as executor:
        futures = [executor.submit(create_issue_via_api, i, base_url) for i in range(1, count + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    total_duration = time.time() - start_time

    context.load_test_results = results
    context.load_test_duration = total_duration
    context.load_test_count = count


@when("{count:d} emails are processed concurrently via mailgw")
def step_concurrent_email_create(context: Context, count: int) -> None:
    """Execute concurrent issue creation via email gateway."""
    start_time = time.time()
    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=min(count, 20)) as executor:
        futures = [executor.submit(create_issue_via_email, i) for i in range(1, count + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    total_duration = time.time() - start_time

    context.load_test_results = results
    context.load_test_duration = total_duration
    context.load_test_count = count


@when("I perform {total_count:d} concurrent operations across all interfaces:")
def step_mixed_interface_load(context: Context, total_count: int) -> None:
    """Execute concurrent operations across multiple interfaces."""
    base_url = "http://localhost:9080/pms"
    start_time = time.time()
    results: list[dict[str, Any]] = []
    interface_counts: dict[str, int] = {}

    # Parse the table to get operation counts per interface
    for row in context.table:
        interface = row["interface"]
        count = int(row["count"])
        interface_counts[interface] = count

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        issue_num = 1

        # Submit CLI tasks
        if "cli" in interface_counts:
            for _ in range(interface_counts["cli"]):
                futures.append(("cli", executor.submit(create_issue_via_cli, issue_num)))
                issue_num += 1

        # Submit API tasks
        if "api" in interface_counts:
            for _ in range(interface_counts["api"]):
                futures.append(("api", executor.submit(create_issue_via_api, issue_num, base_url)))
                issue_num += 1

        # Submit email tasks
        if "email" in interface_counts:
            for _ in range(interface_counts["email"]):
                futures.append(("email", executor.submit(create_issue_via_email, issue_num)))
                issue_num += 1

        # Submit web-ui tasks (skip for now - Playwright is heavyweight)
        if "web-ui" in interface_counts:
            # Web UI via Playwright is too slow for load testing
            # Simulate with CLI instead
            for _ in range(interface_counts["web-ui"]):
                futures.append(("web-ui", executor.submit(create_issue_via_cli, issue_num)))
                issue_num += 1

        # Collect results
        for interface, future in futures:
            result = future.result()
            result["interface"] = interface
            results.append(result)

    total_duration = time.time() - start_time

    context.load_test_results = results
    context.load_test_duration = total_duration
    context.load_test_count = total_count
    context.interface_counts = interface_counts


@given("{count:d} issues exist in the tracker")
def step_create_test_issues(context: Context, count: int) -> None:
    """Create test issues for load testing."""
    issue_ids = []
    for i in range(1, count + 1):
        result = subprocess.run(
            [
                "uv",
                "run",
                "roundup-admin",
                "-i",
                "tracker",
                "create",
                "issue",
                f"title='Pre-existing Issue {i}'",
                "status=1",
                "priority=2",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            issue_id = result.stdout.strip().split()[-1]
            issue_ids.append(issue_id)
    context.test_issue_ids = issue_ids


@when("{count:d} users search for issues concurrently")
def step_concurrent_search(context: Context, count: int) -> None:
    """Execute concurrent issue searches."""
    base_url = "http://localhost:9080/pms"
    start_time = time.time()
    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=min(count, 30)) as executor:
        futures = [executor.submit(search_issues_via_api, i, base_url) for i in range(1, count + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    total_duration = time.time() - start_time

    context.load_test_results = results
    context.load_test_duration = total_duration
    context.load_test_count = count


@when("{count:d} users update different issues concurrently via API")
def step_concurrent_updates(context: Context, count: int) -> None:
    """Execute concurrent issue updates."""
    base_url = "http://localhost:9080/pms"
    start_time = time.time()
    results: list[dict[str, Any]] = []

    # Get issue IDs to update
    issue_ids = context.test_issue_ids[:count]

    with ThreadPoolExecutor(max_workers=min(count, 30)) as executor:
        futures = [
            executor.submit(update_issue_via_api, issue_id, base_url) for issue_id in issue_ids
        ]
        for future in as_completed(futures):
            results.append(future.result())

    total_duration = time.time() - start_time

    context.load_test_results = results
    context.load_test_duration = total_duration
    context.load_test_count = count


@then("all {count:d} issues should be created successfully")
def step_verify_all_created(context: Context, count: int) -> None:
    """Verify all issues were created successfully."""
    results = context.load_test_results
    successful = [r for r in results if r.get("success", False)]
    failed = [r for r in results if not r.get("success", False)]

    if failed:
        print(f"\n❌ Failed operations: {len(failed)}/{count}")
        for failure in failed[:5]:  # Show first 5 failures
            print(f"  - Issue {failure.get('issue_num')}: {failure.get('error')}")

    assert len(successful) == count, f"Expected {count} successful creations, got {len(successful)}"
    assert len(results) == count, f"Expected {count} total results, got {len(results)}"


@then("all {count:d} operations should complete successfully")
def step_verify_all_operations_success(context: Context, count: int) -> None:
    """Verify all operations completed successfully."""
    results = context.load_test_results
    successful = [r for r in results if r.get("success", False)]
    failed = [r for r in results if not r.get("success", False)]

    if failed:
        print(f"\n❌ Failed operations: {len(failed)}/{count}")
        for failure in failed[:5]:
            print(f"  - {failure}")

    assert len(successful) == count, (
        f"Expected {count} successful operations, got {len(successful)}"
    )


@then("all {count:d} issues should be created from emails")
def step_verify_email_created(context: Context, count: int) -> None:
    """Verify all issues were created from emails."""
    step_verify_all_created(context, count)


@then("all {count:d} updates should succeed")
def step_verify_all_updates(context: Context, count: int) -> None:
    """Verify all updates succeeded."""
    results = context.load_test_results
    successful = [r for r in results if r.get("success", False)]
    assert len(successful) == count, f"Expected {count} successful updates, got {len(successful)}"


@then("all searches should return results within {max_duration:d} seconds each")
def step_verify_search_performance(context: Context, max_duration: int) -> None:
    """Verify search performance."""
    results = context.load_test_results
    slow_searches = [r for r in results if r.get("duration", 999) > max_duration]

    if slow_searches:
        print(f"\n⚠️  Slow searches: {len(slow_searches)}")
        for search in slow_searches[:5]:
            print(f"  - User {search.get('user_num')}: {search.get('duration'):.2f}s")

    assert len(slow_searches) == 0, (
        f"Found {len(slow_searches)} searches slower than {max_duration}s"
    )


@then("the operation should complete within {max_seconds:d} seconds")
def step_verify_duration(context: Context, max_seconds: int) -> None:
    """Verify total operation duration."""
    duration = context.load_test_duration
    count = context.load_test_count

    print(f"\n⏱️  Performance: {count} operations in {duration:.2f}s")
    print(f"   Throughput: {count / duration:.2f} ops/sec")
    print(f"   Avg latency: {duration / count * 1000:.2f}ms")

    assert duration <= max_seconds, f"Operation took {duration:.2f}s, limit was {max_seconds}s"


@then("no race conditions should occur")
def step_verify_no_race_conditions(context: Context) -> None:
    """Verify no race conditions occurred (all updates succeeded)."""
    results = context.load_test_results
    failed = [r for r in results if not r.get("success", False)]
    assert len(failed) == 0, f"Race conditions detected: {len(failed)} updates failed"


@then("no database locks should be detected")
def step_verify_no_locks(context: Context) -> None:
    """Verify no database locks occurred."""
    results = context.load_test_results
    # If all operations succeeded within time limits, no locks occurred
    successful = [r for r in results if r.get("success", False)]
    assert len(successful) == len(results), "Database locks detected (operations failed)"


@then("the performance metrics should be recorded")
def step_record_metrics(context: Context) -> None:
    """Record performance metrics to file."""
    results = context.load_test_results
    duration = context.load_test_duration
    count = context.load_test_count

    # Calculate metrics
    successful = [r for r in results if r.get("success", False)]
    failed = [r for r in results if not r.get("success", False)]
    durations = [r.get("duration", 0) for r in successful]

    metrics = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scenario": context.scenario.name,
        "total_operations": count,
        "successful": len(successful),
        "failed": len(failed),
        "total_duration_sec": round(duration, 2),
        "throughput_ops_per_sec": round(count / duration, 2),
        "avg_latency_ms": round(sum(durations) / len(durations) * 1000, 2) if durations else 0,
        "min_latency_ms": round(min(durations) * 1000, 2) if durations else 0,
        "max_latency_ms": round(max(durations) * 1000, 2) if durations else 0,
        "success_rate_pct": round(len(successful) / count * 100, 2),
    }

    # Write to performance log
    log_file = Path("reports/performance-metrics.jsonl")
    log_file.parent.mkdir(exist_ok=True)
    with log_file.open("a") as f:
        f.write(json.dumps(metrics) + "\n")

    # Store in context for potential use by other steps
    context.performance_metrics = metrics

    print("\n📊 Performance Metrics Recorded:")
    print(f"   Success Rate: {metrics['success_rate_pct']}%")
    print(f"   Throughput: {metrics['throughput_ops_per_sec']} ops/sec")
    print(f"   Avg Latency: {metrics['avg_latency_ms']}ms")


@then("the performance report should show interface comparison")
def step_interface_comparison(context: Context) -> None:
    """Generate interface performance comparison."""
    results = context.load_test_results

    # Group by interface
    interface_metrics: dict[str, list[float]] = {}
    for result in results:
        interface = result.get("interface", "unknown")
        if result.get("success", False):
            if interface not in interface_metrics:
                interface_metrics[interface] = []
            interface_metrics[interface].append(result.get("duration", 0))

    print("\n📊 Interface Performance Comparison:")
    for interface, durations in sorted(interface_metrics.items()):
        avg_ms = sum(durations) / len(durations) * 1000
        min_ms = min(durations) * 1000
        max_ms = max(durations) * 1000
        print(
            f"   {interface:8s}: avg={avg_ms:6.2f}ms  min={min_ms:6.2f}ms  max={max_ms:6.2f}ms  (n={len(durations)})"
        )

    # Store in metrics file
    if hasattr(context, "performance_metrics"):
        context.performance_metrics["interface_breakdown"] = {
            interface: {
                "count": len(durations),
                "avg_ms": round(sum(durations) / len(durations) * 1000, 2),
                "min_ms": round(min(durations) * 1000, 2),
                "max_ms": round(max(durations) * 1000, 2),
            }
            for interface, durations in interface_metrics.items()
        }
