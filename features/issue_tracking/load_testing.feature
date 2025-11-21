# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Load Testing and Concurrent Users
  As a sysadmin
  I want performance benchmarks for concurrent users
  So that I can size my deployment appropriately

  Background:
    Given the Roundup tracker is running
    And I am logged in as admin

  @load-test @performance
  Scenario: Load test with 10 concurrent users
    When 10 users create issues concurrently via CLI
    Then all 10 issues should be created successfully
    And the operation should complete within 30 seconds
    And the performance metrics should be recorded

  @load-test @performance
  Scenario: Load test with 50 concurrent users
    When 50 users create issues concurrently via CLI
    Then all 50 issues should be created successfully
    And the operation should complete within 60 seconds
    And the performance metrics should be recorded

  @load-test @performance
  Scenario: Load test with 100 concurrent issues
    When 100 issues are created concurrently via API
    Then all 100 issues should be created successfully
    And the operation should complete within 120 seconds
    And the performance metrics should be recorded

  @load-test @performance
  Scenario: Concurrent email processing
    When 20 emails are processed concurrently via mailgw
    Then all 20 issues should be created from emails
    And the operation should complete within 45 seconds
    And the performance metrics should be recorded

  @load-test @performance
  Scenario: Mixed interface load test
    When I perform 50 concurrent operations across all interfaces:
      | interface | operation     | count |
      | web-ui    | create_issue  | 10    |
      | cli       | create_issue  | 15    |
      | api       | create_issue  | 15    |
      | email     | create_issue  | 10    |
    Then all 50 operations should complete successfully
    And the operation should complete within 90 seconds
    And the performance metrics should be recorded
    And the performance report should show interface comparison

  @load-test @performance
  Scenario: Database query performance under load
    Given 100 issues exist in the tracker
    When 20 users search for issues concurrently
    Then all searches should return results within 5 seconds each
    And no database locks should be detected
    And the performance metrics should be recorded

  @load-test @performance
  Scenario: Concurrent issue updates
    Given 50 issues exist in the tracker
    When 25 users update different issues concurrently via API
    Then all 25 updates should succeed
    And no race conditions should occur
    And the operation should complete within 45 seconds
    And the performance metrics should be recorded
