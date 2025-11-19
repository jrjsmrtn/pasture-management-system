# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-1
Feature: Issue Status Workflow
  As a homelab sysadmin
  I want issues to move through defined statuses
  So that I can track progress on resolving problems

  Background:
    Given the Roundup tracker is running

  @web-ui @smoke
  Scenario: Transition issue from New to In Progress
    Given I am logged in to the web UI as "admin" with password "admin"
    And an issue exists with title "Network connectivity problem" and status "new"
    When I view the issue details
    And I click "Start Work"
    Then the issue status should be "in-progress"
    And I should see "status edited ok"
    And the status change should be recorded in history

  @web-ui @validation
  Scenario: Cannot transition from New to Closed directly
    Given I am logged in to the web UI as "admin" with password "admin"
    And an issue exists with title "Security vulnerability" and status "new"
    When I view the issue details
    Then I should not see "Close Issue" button
    And only valid transitions should be available

  @cli
  Scenario: Update issue status via CLI
    Given an issue exists with ID "1" and status "new"
    When I run roundup command "set issue1 status=in-progress"
    Then the command should succeed
    And issue "1" should have status "in-progress"

  @api
  Scenario: Transition issue via API
    Given I have a valid API token
    And an issue exists with title "Database backup failed" and status "in-progress"
    When I PATCH the current issue via API with JSON:
      """
      {
        "status": "resolved"
      }
      """
    Then the response status should be 200
    And the issue status should be "resolved"

  @web-ui
  Scenario: View status history
    Given I am logged in to the web UI as "admin" with password "admin"
    And an issue exists with title "Disk space low" and status "new"
    And the issue status was changed to "in-progress" at "2025-11-15 10:00:00"
    And the issue status was changed to "resolved" at "2025-11-15 14:30:00"
    When I view the issue details
    Then I should see "History"

  @web-ui @validation
  Scenario: Complete workflow from New to Closed
    Given I am logged in to the web UI as "admin" with password "admin"
    And an issue exists with title "Email server down" and status "new"
    When I view the issue details
    And I click "Start Work"
    Then the issue status should be "in-progress"
    When I click "Mark Resolved"
    Then the issue status should be "resolved"
    When I click "Close Issue"
    Then the issue status should be "closed"

  @api @validation
  Scenario: Invalid status transition is rejected
    Given I have a valid API token
    And an issue exists with title "Firewall misconfiguration" and status "new"
    When I PATCH the current issue via API with JSON:
      """
      {
        "status": "closed"
      }
      """
    Then the response status should be 405
    And the response should contain error "Invalid status transition: new -> closed"
