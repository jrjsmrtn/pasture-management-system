# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Email Notification System
  As a homelab sysadmin
  I want email notifications when issues are updated
  So that I can stay informed without checking the web interface

  Background:
    Given the Roundup tracker is running
    And the admin user exists with email "roundup-admin@localhost"
    And the email debug log is cleared

  @smoke @notifications
  Scenario: Send notification on issue creation
    Given I create an issue with title "Database backup failed" via CLI
    When I check the email debug log
    Then an email notification should have been sent
    And the notification subject should contain "Database backup failed"
    And the notification should be sent to "roundup-admin@localhost"
    And the notification should contain the issue link

  @notifications
  Scenario: Send notification on issue update
    Given an issue exists with id "1" and title "Server maintenance"
    When I add a message to issue "1" with content "Starting maintenance now"
    And I check the email debug log
    Then an email notification should have been sent
    And the notification subject should contain "Server maintenance"
    And the notification body should contain "Starting maintenance now"
    And the notification should contain the issue link

  @notifications
  Scenario: Send notification on status change
    Given an issue exists with id "1" and title "Deploy new monitoring"
    When I update issue "1" status to "in-progress"
    And I check the email debug log
    Then an email notification should have been sent
    And the notification subject should contain "Deploy new monitoring"
    And the notification body should contain "in-progress"
    And the notification should contain the issue link

  @notifications
  Scenario: Send notification on priority change
    Given an issue exists with id "1" and title "Security patch needed"
    When I update issue "1" priority to "urgent"
    And I check the email debug log
    Then an email notification should have been sent
    And the notification subject should contain "Security patch needed"
    And the notification body should contain "urgent"

  @notifications
  Scenario: Multiple recipients on nosy list
    Given an issue exists with id "1" and title "System upgrade"
    And user "alice@localhost" is on the nosy list for issue "1"
    And user "bob@localhost" is on the nosy list for issue "1"
    When I add a message to issue "1" with content "Upgrade scheduled for tonight"
    And I check the email debug log
    Then email notifications should have been sent to:
      | recipient           |
      | alice@localhost     |
      | bob@localhost       |

  @notifications
  Scenario: Notification includes issue metadata
    Given I create an issue with title "Network outage" via CLI
    When I check the email debug log
    Then an email notification should have been sent
    And the notification should contain:
      | field          | value           |
      | Issue ID       | 1               |
      | Title          | Network outage  |
      | Status         | new             |
      | Creator        | admin           |

  @notifications @config @manual
  Scenario: Nosy list auto-adds creator (Manual Test - Config Dependent)
    # Sprint 9 Story 3: CLI bypasses reactor/auditor system (architectural limitation)
    # This scenario requires roundup-admin CLI which doesn't trigger notification hooks
    # Manual verification: Create issue via Web UI and verify nosy list behavior
    Given nosy configuration is set to "add_author = new"
    When I create an issue with title "Auto-add test" via CLI
    And I check the nosy list for the created issue
    Then the creator should be on the nosy list
    And an email notification should have been sent to the creator

  @notifications @config @manual
  Scenario: Message author not notified (Manual Test - Config Dependent)
    # Sprint 9 Story 3: Requires dynamic config.ini change + server restart during test
    # This is a Roundup built-in feature, not custom code to test
    # Manual verification: Set messages_to_author = no in config, restart, test manually
    Given nosy configuration is set to "messages_to_author = no"
    And an issue exists with id "1" and title "Self-update test"
    And the admin user is on the nosy list for issue "1"
    When I add a message to issue "1" with content "I am updating my own issue"
    And I check the email debug log
    Then no email notification should have been sent to "roundup-admin@localhost"
