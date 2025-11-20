# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Four-Interface BDD Testing
  As a developer
  I want to test issue management across Web UI, CLI, API, and Email interfaces
  So that I can ensure consistent behavior and complete test coverage

  Background:
    Given the Roundup tracker is running
    And the admin user exists with email "roundup-admin@localhost"

  # ============================================================================
  # Issue Creation - All 4 Interfaces
  # ============================================================================

  @four-interface @web-ui @smoke
  Scenario: Create issue via Web UI
    Given I am logged in as "admin" with password "admin"
    When I navigate to the new issue page
    And I fill in the issue form:
      | field    | value                     |
      | title    | Web UI Test Issue         |
      | priority | urgent                    |
    And I submit the form
    Then I should see "Web UI Test Issue" on the page
    And the issue should be created in the database

  @four-interface @cli @smoke
  Scenario: Create issue via CLI
    When I create an issue via CLI with:
      | field    | value                |
      | title    | CLI Test Issue       |
      | priority | urgent               |
    Then the issue should be created
    And the issue title should be "CLI Test Issue"
    And the issue priority should be "urgent"

  @four-interface @api @smoke
  Scenario: Create issue via API
    When I create an issue via API with:
      | field    | value                |
      | title    | API Test Issue       |
      | priority | urgent               |
    Then the API response should be successful
    And the issue should be created in the database
    And the issue title should be "API Test Issue"
    And the issue priority should be "urgent"

  @four-interface @email @smoke
  Scenario: Create issue via Email
    Given I compose an email with:
      | field   | value                                      |
      | from    | roundup-admin@localhost                    |
      | to      | issue_tracker@localhost                    |
      | subject | Email Test Issue [priority=urgent]        |
      | body    | This issue was created via email gateway  |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue title should be "Email Test Issue"
    And the issue priority should be "urgent"

  # ============================================================================
  # Issue Updates - All 4 Interfaces
  # ============================================================================

  @four-interface @web-ui
  Scenario: Update issue via Web UI
    Given an issue exists with id "1" and title "Web UI Update Test"
    And I am logged in as "admin" with password "admin"
    When I navigate to issue "1"
    And I update the issue status to "in-progress"
    And I submit the form
    Then I should see "in-progress" on the page
    And the issue "1" status should be "in-progress"

  @four-interface @cli
  Scenario: Update issue via CLI
    Given an issue exists with id "1" and title "CLI Update Test"
    When I update issue "1" status to "in-progress" via CLI
    Then the issue "1" status should be "in-progress"

  @four-interface @api
  Scenario: Update issue via API
    Given an issue exists with id "1" and title "API Update Test"
    When I update issue "1" via API with:
      | field  | value       |
      | status | in-progress |
    Then the API response should be successful
    And the issue "1" status should be "in-progress"

  @four-interface @email
  Scenario: Update issue via Email
    Given an issue exists with id "1" and title "Email Update Test"
    When I compose an email with:
      | field   | value                                       |
      | from    | roundup-admin@localhost                     |
      | to      | issue_tracker@localhost                     |
      | subject | [issue1] Email Update Test                  |
      | body    | Updating this issue via email               |
    And I send the email to the mail gateway
    Then the issue "1" should have a new message
    And the new message should contain "Updating this issue via email"

  # ============================================================================
  # Property Setting - All 4 Interfaces
  # ============================================================================

  @four-interface @web-ui
  Scenario: Set priority via Web UI
    Given an issue exists with id "1" and title "Web Priority Test"
    And I am logged in as "admin" with password "admin"
    When I navigate to issue "1"
    And I select priority "critical"
    And I submit the form
    Then the issue "1" priority should be "critical"

  @four-interface @cli
  Scenario: Set priority via CLI
    Given an issue exists with id "1" and title "CLI Priority Test"
    When I set issue "1" priority to "critical" via CLI
    Then the issue "1" priority should be "critical"

  @four-interface @api
  Scenario: Set priority via API
    Given an issue exists with id "1" and title "API Priority Test"
    When I update issue "1" via API with:
      | field    | value    |
      | priority | critical |
    Then the API response should be successful
    And the issue "1" priority should be "critical"

  @four-interface @email
  Scenario: Set priority via Email
    Given I compose an email with:
      | field   | value                                      |
      | from    | roundup-admin@localhost                    |
      | to      | issue_tracker@localhost                    |
      | subject | Email Priority Test [priority=critical]   |
      | body    | Setting priority via email                 |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue priority should be "critical"

  # ============================================================================
  # Cross-Interface Verification
  # ============================================================================

  @four-interface @integration
  Scenario: Create via Email, verify via Web UI
    Given I compose an email with:
      | field   | value                              |
      | from    | roundup-admin@localhost            |
      | to      | issue_tracker@localhost            |
      | subject | Cross-interface Test Issue         |
      | body    | Created via email, verified via UI |
    When I send the email to the mail gateway
    Then a new issue should be created
    And I am logged in as "admin" with password "admin"
    And I navigate to the issues list
    And I should see "Cross-interface Test Issue" on the page

  @four-interface @integration
  Scenario: Create via CLI, update via API, verify via Web UI
    When I create an issue via CLI with:
      | field | value                |
      | title | Multi-interface Test |
    Then the issue should be created
    When I update the last created issue via API with:
      | field  | value       |
      | status | in-progress |
    Then the API response should be successful
    And I am logged in as "admin" with password "admin"
    And I navigate to the last created issue
    And I should see "in-progress" on the page

  @four-interface @integration
  Scenario: Create via API, add message via Email, verify via CLI
    When I create an issue via API with:
      | field | value           |
      | title | API Email Test  |
    Then the API response should be successful
    And I note the created issue ID as "api_issue"
    When I compose an email with:
      | field   | value                                |
      | from    | roundup-admin@localhost              |
      | to      | issue_tracker@localhost              |
      | subject | [{api_issue}] API Email Test         |
      | body    | Adding message via email             |
    And I send the email to the mail gateway
    Then the issue "{api_issue}" should have a new message
    And I verify via CLI that issue "{api_issue}" has the message

  # ============================================================================
  # Coverage Summary Scenario
  # ============================================================================

  @four-interface @summary
  Scenario: Four-interface coverage demonstration
    # This scenario demonstrates that we have complete BDD coverage
    # across all 4 interfaces for the core issue management operations

    # Operation 1: Create issues
    When I create issues via all interfaces:
      | interface | title            |
      | Web UI    | Web Created      |
      | CLI       | CLI Created      |
      | API       | API Created      |
      | Email     | Email Created    |
    Then all 4 issues should exist in the database

    # Operation 2: Update issues
    When I update all issues to status "in-progress" via all interfaces
    Then all 4 issues should have status "in-progress"

    # Operation 3: Set properties
    When I set priority "critical" on all issues via all interfaces
    Then all 4 issues should have priority "critical"

    # Verification: Complete test coverage achieved
    And the BDD test coverage should include all 4 interfaces
