# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Email Gateway Integration
  As a homelab sysadmin
  I want to create and update issues via email
  So that I can manage my homelab from my email client

  Background:
    Given the Roundup tracker is running
    And the admin user exists with email "roundup-admin@localhost"

  @smoke @email
  Scenario: Create issue from plain text email
    Given I compose an email with:
      | field   | value                                |
      | from    | roundup-admin@localhost              |
      | to      | issue_tracker@localhost              |
      | subject | Server backup failure                |
      | body    | The nightly backup job failed at 2am |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue title should be "Server backup failure"
    And the issue description should contain "The nightly backup job failed at 2am"

  @smoke @email
  Scenario: Update existing issue via email
    Given an issue exists with id "1" and title "Server backup failure"
    And I compose an email with:
      | field   | value                                         |
      | from    | roundup-admin@localhost                               |
      | to      | issue_tracker@localhost                       |
      | subject | [issue1] Server backup failure                |
      | body    | I checked the logs and found the root cause   |
    When I send the email to the mail gateway
    Then the issue "1" should have a new message
    And the new message should contain "I checked the logs and found the root cause"
    And the issue status should not be "closed"

  @email
  Scenario: Create issue with priority set via email
    Given I compose an email with:
      | field   | value                                     |
      | from    | roundup-admin@localhost                           |
      | to      | issue_tracker@localhost                   |
      | subject | Network outage detected [priority=urgent] |
      | body    | All services are unreachable              |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue title should be "Network outage detected"
    And the issue priority should be "urgent"

  @email
  Scenario: Update issue status via email subject
    Given I create an issue with title "Task to work on" via email
    And I note the issue ID as "work_issue"
    And I compose an email with:
      | field   | value                                      |
      | from    | roundup-admin@localhost                    |
      | to      | issue_tracker@localhost                    |
      | subject | [{work_issue}] Working on this [status=in-progress] |
      | body    | Working on this issue now                  |
    When I send the email to the mail gateway
    Then the issue "{work_issue}" status should be "in-progress"
    And the issue "{work_issue}" should have a new message

  @email
  Scenario: Email with quoted text is handled correctly
    Given I create an issue with title "Database slow queries" via email
    And I note the issue ID as "db_issue"
    And I compose an email with:
      | field   | value                                                                    |
      | from    | roundup-admin@localhost                                                  |
      | to      | issue_tracker@localhost                                                  |
      | subject | [{db_issue}] Database slow queries                                       |
      | body    | I optimized the query.\n\n> Original message:\n> The database is slow |
    When I send the email to the mail gateway
    Then the issue "{db_issue}" should have a new message
    And the new message should contain "I optimized the query"
    And the new message should contain "> Original message:"

  @email @validation @security
  Scenario: Email from unknown user is silently rejected for security
    Given no user exists with email "newuser@localhost"
    And I compose an email with:
      | field   | value                          |
      | from    | newuser@localhost              |
      | to      | issue_tracker@localhost        |
      | subject | Request: Add monitoring tool   |
      | body    | Please add Prometheus monitoring |
    When I send the email to the mail gateway
    Then no user should be created with email "newuser@localhost"
    And no issue should be created
    # Note: Silent rejection (no error response) prevents email enumeration attacks

  @email @validation @security
  Scenario: Email with invalid issue ID is silently rejected for security
    Given I compose an email with:
      | field   | value                           |
      | from    | roundup-admin@localhost         |
      | to      | issue_tracker@localhost         |
      | subject | [issue99999] Non-existent issue |
      | body    | This issue does not exist       |
    When I send the email to the mail gateway
    Then no issue should be created
    # Note: Silent rejection prevents issue ID enumeration attacks

  @email @skip
  Scenario: Email with multiple attachments (Future Enhancement - Sprint 9 Story 2)
    # Descoped in Sprint 9 - Email attachments require MIME multipart/mixed parsing
    # Web UI provides alternative attachment mechanism
    # See Sprint 9 retrospective for details
    Given I compose an email with:
      | field       | value                              |
      | from        | roundup-admin@localhost            |
      | to          | issue_tracker@localhost            |
      | subject     | Firewall configuration issue       |
      | body        | See attached logs and config files |
      | attachments | firewall.log, firewall.conf        |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue should have 2 attachments
    And the attachments should be named "firewall.log" and "firewall.conf"

  @email @html
  Scenario: HTML email is converted to plain text
    Given I compose an HTML email with:
      | field   | value                                      |
      | from    | roundup-admin@localhost                            |
      | to      | issue_tracker@localhost                    |
      | subject | SSL certificate expiring                   |
      | html    | <p>The SSL cert expires in <b>7 days</b></p> |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue description should contain "The SSL cert expires in 7 days"
    And the issue description should not contain "<p>" or "<b>"
