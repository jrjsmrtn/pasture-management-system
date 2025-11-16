# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-4
Feature: Create Change Request
  As a homelab sysadmin
  I want to create change requests
  So that I can plan and track infrastructure changes

  Background:
    Given the Roundup tracker is running

  @web-ui @smoke
  Scenario: Create change request with required fields
    Given I am logged in to the web UI as "admin" with password "admin"
    When I navigate to the "New Change" page
    And I enter the following change details:
      | field         | value                                    |
      | title         | Upgrade database server to PostgreSQL 16 |
      | justification | Security patches and performance improvements |
      | impact        | 2-hour maintenance window required        |
      | risk          | Low - tested in staging environment      |
      | priority      | high                                      |
      | category      | software                                  |
    And I submit the change
    Then I should see a success message
    And the change should be saved with title "Upgrade database server to PostgreSQL 16"

  @web-ui @validation
  Scenario: Cannot create change without justification
    Given I am logged in to the web UI as "admin" with password "admin"
    When I navigate to the "New Change" page
    And I enter the following change details:
      | field    | value                           |
      | title    | Update firewall rules           |
      | priority | medium                          |
      | category | configuration                   |
    And I submit the change
    Then I should see an error message about required fields

  @cli
  Scenario: Create change via CLI
    Given I have CLI access to the tracker
    When I create a change via CLI with:
      | field         | value                                  |
      | title         | Migrate email server to new hardware   |
      | justification | Current server approaching end-of-life |
      | priority      | high                                   |
      | category      | hardware                               |
    Then the change should be created successfully
    And the change should have status "proposed"

  @api
  Scenario: Create change via API
    Given I have a valid API token
    When I POST to "/rest/data/change" with JSON:
      """
      {
        "title": "Implement network segmentation",
        "justification": "Improve security posture and compliance",
        "impact": "Temporary network interruptions during implementation",
        "risk": "Medium - requires careful planning",
        "priority": "3",
        "category": "4"
      }
      """
    Then the response status should be 201
    And the response should contain the created change ID
