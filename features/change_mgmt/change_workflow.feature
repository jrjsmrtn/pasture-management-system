# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Change Approval Workflow
  As a homelab sysadmin
  I want changes to go through approval stages
  So that I can prevent unauthorized or risky changes

  Background:
    Given the Roundup tracker is running
    And I am logged in to the web UI as "admin"

  @story-1 @web-ui @smoke
  Scenario: Approve change request through workflow stages
    Given a change exists with title "Upgrade PostgreSQL" and status "planning"
    When I view the change details
    And I click "Start Assessment"
    Then the change status should be "approved"
    When I add assessment notes "Risk: Low, Impact: Minimal downtime"
    And I click "Approve"
    Then the change status should be "approved"
    And I should see "Change approved successfully"
    And the status change should be recorded in history

  @story-1 @web-ui @validation
  Scenario: Cannot skip assessment stage
    Given a change exists with title "Network reconfiguration" and status "planning"
    When I view the change details
    Then I should not see "Approve" button
    And I should only see "Start Assessment" button

  @story-1 @web-ui
  Scenario: Reject change with reason
    Given a change exists with title "Risky upgrade" and status "approved"
    When I view the change details
    And I click "Reject"
    And I enter rejection reason "Conflicts with security policy"
    And I confirm rejection
    Then the change status should be "cancelled"
    And the rejection reason should be recorded
    And I should see "Change rejected: Conflicts with security policy"

  @story-1 @web-ui
  Scenario: Complete change workflow from planning to completed
    Given a change exists with title "Database backup schedule" and status "planning"
    When I view the change details
    And I click "Approve"
    Then the change status should be "approved"
    When I click "Schedule"
    And I enter scheduled date "2025-12-15 02:00"
    And I click "Save Schedule"
    Then the change status should be "implementing"
    When I click "Start Implementation"
    Then the change status should be "implementing"
    When I enter implementation notes "Backup schedule updated successfully"
    And I click "Mark Complete"
    Then the change status should be "completed"
    And I should see "Change completed successfully"

  @story-1 @cli
  Scenario: Update change status via CLI
    Given a change exists with ID "1" and status "approved"
    When I run "roundup-admin -i tracker set change1 status=implementing"
    Then the command should succeed
    And change "1" should have status "implementing"

  @story-1 @cli
  Scenario: Add notes when changing status via CLI
    Given a change exists with ID "1" and status "approved"
    When I run "roundup-admin -i tracker set change1 status=implementing messages='Starting implementation now'"
    Then the command should succeed
    And change "1" should have status "implementing"
    And the change should have a message containing "Starting implementation now"

  @story-1 @api
  Scenario: Complete change implementation via API
    Given a change exists with ID "1" and status "implementing"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "status": "4",
        "messages": [{"content": "Database upgraded successfully, all tests passed"}]
      }
      """
    Then the response status should be 200
    And change "1" should have status "completed"
    And the change should have a message containing "Database upgraded successfully"

  @story-1 @api
  Scenario: Cannot skip workflow stages via API
    Given a change exists with ID "1" and status "planning"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "status": "4"
      }
      """
    Then the response status should be 400
    And the response should contain "Invalid status transition"
    And change "1" should have status "planning"

  @story-1 @api
  Scenario: View change status history via API
    Given a change exists with ID "1" and status "completed"
    And the change has gone through workflow stages
    When I GET "/api/change1"
    Then the response status should be 200
    And the response should contain status history
    And the history should show transitions: "planning" -> "approved" -> "implementing" -> "completed"
