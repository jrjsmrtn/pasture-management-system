# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-5 @change-management
Feature: View Change List
  As a homelab sysadmin
  I want to see all change requests
  So that I can track planned infrastructure changes

  Background:
    Given I am logged in to the web UI

  @web-ui
  Scenario: View list of changes
    Given the following changes exist:
      | title              | priority | category      |
      | Database upgrade   | High     | Software      |
      | Network reconfig   | Medium   | Network       |
      | Add disk space     | Low      | Hardware      |
    When I navigate to "Changes"
    Then I should see 3 changes
    And "Database upgrade" should appear before "Network reconfig"

  @web-ui
  Scenario: Filter changes by category
    Given the following changes exist:
      | title              | category      |
      | Database upgrade   | Software      |
      | Network reconfig   | Network       |
      | Add disk space     | Hardware      |
    When I navigate to "Changes"
    And I filter by category "Software"
    Then I should see 1 change
    And I should see "Database upgrade"

  @web-ui
  Scenario: Filter changes by priority
    Given the following changes exist:
      | title              | priority |
      | Critical fix       | Critical |
      | Database upgrade   | High     |
      | Network reconfig   | Medium   |
      | Add disk space     | Low      |
    When I navigate to "Changes"
    And I filter by priority "High"
    Then I should see 1 change
    And I should see "Database upgrade"

  @web-ui
  Scenario: Filter changes by status
    Given the following changes exist:
      | title              | status   |
      | Database upgrade   | Planning |
      | Network reconfig   | Approved |
      | Add disk space     | Planning |
    When I navigate to "Changes"
    And I filter by status "Planning"
    Then I should see 2 changes
    And I should see "Database upgrade"
    And I should see "Add disk space"

  @web-ui
  Scenario: Changes sorted by priority then creation date
    Given the following changes exist:
      | title            | priority | created_date |
      | Low priority 1   | Low      | 2025-11-15   |
      | High priority 1  | High     | 2025-11-16   |
      | High priority 2  | High     | 2025-11-15   |
      | Medium priority  | Medium   | 2025-11-16   |
    When I navigate to "Changes"
    Then the changes should appear in order:
      | title            |
      | High priority 2  |
      | High priority 1  |
      | Medium priority  |
      | Low priority 1   |

  @web-ui
  Scenario: Click change to view details
    Given the following changes exist:
      | title              | description                   |
      | Database upgrade   | Upgrade PostgreSQL to v16     |
    When I navigate to "Changes"
    And I click on "Database upgrade"
    Then I should see the change details page
    And I should see "Upgrade PostgreSQL to v16"

  @web-ui
  Scenario: Empty change list displays helpful message
    Given no changes exist
    When I navigate to "Changes"
    Then I should see "No change requests found"
    And I should see a "Create New Change" button

  @cli
  Scenario: List all changes via CLI
    Given the following changes exist:
      | title              | priority |
      | Database upgrade   | High     |
      | Network reconfig   | Medium   |
    When I run "roundup-client list change"
    Then the command should succeed
    And I should see "Database upgrade"
    And I should see "Network reconfig"

  @cli
  Scenario: Filter changes by category via CLI
    Given the following changes exist:
      | title              | category |
      | Database upgrade   | Software |
      | Network reconfig   | Network  |
    When I run "roundup-client list change category=software"
    Then the command should succeed
    And I should see "Database upgrade"
    And I should not see "Network reconfig" in CLI output

  @api
  Scenario: Get all changes via API
    Given I have a valid API token
    And the following changes exist:
      | title              | priority |
      | Database upgrade   | High     |
      | Network reconfig   | Medium   |
    When I GET "/api/changes"
    Then the response status should be 200
    And the response should contain 2 changes
    And the response should include "Database upgrade"

  @api
  Scenario: Filter changes by priority via API
    Given I have a valid API token
    And the following changes exist:
      | title              | priority |
      | Critical fix       | Critical |
      | Database upgrade   | High     |
      | Network reconfig   | Medium   |
    When I GET "/api/changes?priority=critical"
    Then the response status should be 200
    And the response should contain 1 change
    And the response should include "Critical fix"

  @api
  Scenario: Changes returned sorted by priority
    Given I have a valid API token
    And the following changes exist:
      | title              | priority |
      | Low priority       | Low      |
      | High priority      | High     |
      | Medium priority    | Medium   |
    When I GET "/api/changes"
    Then the response status should be 200
    And the first change should be "High priority"
    And the last change should be "Low priority"
