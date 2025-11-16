# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Change Implementation Tracking
  As a homelab sysadmin
  I want to track change implementation progress
  So that I can document what was actually done

  Background:
    Given the Roundup tracker is running
    And I am logged in to the web UI as "admin"

  @story-5 @web-ui @smoke
  Scenario: Begin change implementation
    Given a change exists with title "Database upgrade" and status "scheduled"
    And the change is scheduled for "2025-11-20 02:00" to "2025-11-20 04:00"
    When I view the change details
    And I click "Start Implementation"
    Then the change status should be "implementing"
    And the change should have actual start time recorded

  @story-5 @web-ui
  Scenario: Complete change with implementation notes
    Given a change exists with title "Server patching" and status "implementing"
    When I view the change details
    And I fill in implementation notes:
      | Field                  | Value                                                    |
      | Implementation Notes   | Upgraded database from v15 to v16. Migration took 45 min |
      | Actual Duration        | 45 minutes                                               |
    And I click "Mark Complete"
    Then the change status should be "completed"
    And the change should have actual end time recorded
    And I should see "Upgraded database from v15 to v16"

  @story-5 @web-ui
  Scenario: Document deviation from plan
    Given a change exists with title "Network reconfiguration" and status "implementing"
    And the change was scheduled for 2 hours
    When I view the change details
    And I fill in implementation notes:
      | Field              | Value                                        |
      | Implementation Notes | Config more complex than planned             |
      | Deviation Notes    | Took 3 hours instead of 2, needed extra time |
    And I click "Mark Complete"
    Then the change status should be "completed"
    And I should see "Took 3 hours instead of 2"
    And the deviation should be recorded

  @story-5 @web-ui
  Scenario: Document change rollback
    Given a change exists with title "Application deployment" and status "implementing"
    When I view the change details
    And I click "Rollback"
    And I enter rollback reason "Migration failed validation tests"
    And I enter rollback notes "Restored from backup, downtime was 30 minutes"
    And I confirm rollback
    Then the change status should be "cancelled"
    And I should see "Migration failed validation tests"
    And the rollback should be documented

  @story-5 @web-ui
  Scenario: View actual vs scheduled times
    Given a change exists with title "Firmware update" and status "completed"
    And the change was scheduled for "2025-11-18 02:00" to "2025-11-18 03:00"
    And the change actual times were "2025-11-18 02:05" to "2025-11-18 03:15"
    When I view the change details
    Then I should see "Scheduled Start" section with "2025-11-18 02:00"
    And I should see "Actual Start" section with "2025-11-18 02:05"
    And I should see "Scheduled End" section with "2025-11-18 03:00"
    And I should see "Actual End" section with "2025-11-18 03:15"

  @story-5 @web-ui
  Scenario: Track implementation success
    Given a change exists with title "Security patches" and status "implementing"
    When I view the change details
    And I select implementation outcome "Success"
    And I enter implementation notes "All patches applied successfully, no issues"
    And I click "Mark Complete"
    Then the change status should be "completed"
    And the implementation outcome should be "Success"

  @story-5 @cli
  Scenario: Start implementation via CLI
    Given a change exists with ID "1" and status "scheduled"
    When I run "roundup-admin -i tracker set change1 status=implementing actual_start='2025-11-20.02:00:00'"
    Then the command should succeed
    And change "1" should have status "implementing"
    And change "1" should have actual start time

  @story-5 @cli
  Scenario: Complete implementation via CLI
    Given a change exists with ID "1" and status "implementing"
    When I run "roundup-admin -i tracker set change1 status=completed actual_end='2025-11-20.04:00:00' implementation_notes='Successfully completed'"
    Then the command should succeed
    And change "1" should have status "completed"
    And change "1" should have implementation notes

  @story-5 @cli
  Scenario: View implementation details via CLI
    Given a change exists with ID "1" and status "completed"
    And the change has implementation notes "Database upgraded successfully"
    When I run "roundup-admin -i tracker get change1 implementation_notes actual_start actual_end"
    Then the command should succeed
    And the output should contain "Database upgraded successfully"
    And the output should contain actual start time
    And the output should contain actual end time

  @story-5 @api
  Scenario: Start implementation via API
    Given a change exists with ID "1" and status "scheduled"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "status": "implementing",
        "actual_start": "2025-11-20.02:00:00"
      }
      """
    Then the response status should be 200
    And the change should have status "implementing"
    And the change should have actual start time

  @story-5 @api
  Scenario: Complete implementation via API
    Given a change exists with ID "1" and status "implementing"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "status": "completed",
        "actual_end": "2025-11-20.04:00:00",
        "implementation_notes": "Upgrade completed successfully. All tests passed."
      }
      """
    Then the response status should be 200
    And the change should have status "completed"
    And the change should have implementation notes

  @story-5 @api
  Scenario: Document rollback via API
    Given a change exists with ID "1" and status "implementing"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "status": "cancelled",
        "rollback_reason": "Critical bug discovered during deployment",
        "rollback_notes": "Reverted to previous version, all services restored"
      }
      """
    Then the response status should be 200
    And the change should have status "cancelled"
    And the change should have rollback documentation

  @story-5 @api
  Scenario: Get implementation details via API
    Given a change exists with ID "1" and status "completed"
    And the change has implementation notes "System upgrade successful"
    When I GET "/api/change1"
    Then the response status should be 200
    And the response should include "implementation_notes"
    And the response should include "actual_start"
    And the response should include "actual_end"
    And the implementation notes should be "System upgrade successful"
