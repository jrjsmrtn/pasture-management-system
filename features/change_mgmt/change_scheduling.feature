# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Change Scheduling
  As a homelab sysadmin
  I want to schedule approved changes for specific times
  So that I can plan maintenance windows

  Background:
    Given the Roundup tracker is running
    And I am logged in to the web UI as "admin"

  @story-4 @web-ui @smoke
  Scenario: Schedule approved change
    Given a change exists with title "Database upgrade" and status "approved"
    When I view the change details
    And I fill in scheduling information:
      | Field          | Value      |
      | Scheduled Date | 2025-12-01 |
      | Start Time     | 02:00      |
      | End Time       | 04:00      |
    And I click "Submit"
    Then the change should have scheduled times
    And I should see scheduled start "2025-12-01 02:00"
    And I should see scheduled end "2025-12-01 04:00"

  @story-4 @web-ui
  Scenario: Reschedule change
    Given a change exists with title "Network maintenance" and status "scheduled"
    And the change is scheduled for "2025-12-01 02:00" to "2025-12-01 04:00"
    When I view the change details
    And I update the scheduled date to "2025-12-08"
    And I click "Submit"
    Then I should see scheduled start "2025-12-08 02:00"
    And the schedule change should be recorded in history

  @story-4 @web-ui
  Scenario: View scheduled time on change details
    Given a change exists with title "Server reboot" and status "scheduled"
    And the change is scheduled for "2025-11-20 03:00" to "2025-11-20 03:30"
    When I view the change details
    Then I should see "Scheduled Start" section
    And I should see "2025-11-20 03:00"
    And I should see "Scheduled End" section
    And I should see "2025-11-20 03:30"

  @story-4 @web-ui
  Scenario: Schedule shows in change list
    Given the following changes exist:
      | title              | status    | scheduled_start  | scheduled_end    |
      | Patch server       | scheduled | 2025-11-25 01:00 | 2025-11-25 02:00 |
      | Update firewall    | scheduled | 2025-11-26 02:00 | 2025-11-26 03:00 |
      | Backup restore     | scheduled | 2025-11-27 03:00 | 2025-11-27 05:00 |
    When I navigate to "Changes"
    Then I should see all 3 changes listed
    And the changes should show their scheduled times

  @story-4 @cli
  Scenario: Schedule change via CLI
    Given a change exists with ID "1" and status "approved"
    When I run "roundup-admin -i tracker set change1 scheduled_start='2025-12-01.02:00:00' scheduled_end='2025-12-01.04:00:00'"
    Then the command should succeed
    And change "1" should have scheduled start time
    And change "1" should have scheduled end time

  @story-4 @cli
  Scenario: View schedule via CLI
    Given a change exists with ID "1" and status "scheduled"
    And the change is scheduled for "2025-12-01 02:00" to "2025-12-01 04:00"
    When I run "roundup-admin -i tracker get change1 scheduled_start scheduled_end"
    Then the command should succeed
    And the output should contain "2025-12-01.02:00:00"
    And the output should contain "2025-12-01.04:00:00"

  @story-4 @api
  Scenario: Schedule change via API
    Given a change exists with ID "1" and status "approved"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "scheduled_start": "2025-12-01.02:00:00",
        "scheduled_end": "2025-12-01.04:00:00"
      }
      """
    Then the response status should be 200
    And the change should have scheduled start time
    And the change should have scheduled end time

  @story-4 @api
  Scenario: Reschedule via API
    Given a change exists with ID "1" and status "scheduled"
    And the change is scheduled for "2025-12-01 02:00" to "2025-12-01 04:00"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "scheduled_start": "2025-12-08.02:00:00"
      }
      """
    Then the response status should be 200
    And the change should have updated scheduled start time

  @story-4 @api
  Scenario: Get scheduled change via API
    Given a change exists with ID "1" and status "scheduled"
    And the change is scheduled for "2025-12-01 02:00" to "2025-12-01 04:00"
    When I GET "/api/change1"
    Then the response status should be 200
    And the response should include "scheduled_start"
    And the response should include "scheduled_end"
    And the scheduled start should be "2025-12-01.02:00:00"
    And the scheduled end should be "2025-12-01.04:00:00"
