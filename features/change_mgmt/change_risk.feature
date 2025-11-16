# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Change Risk Assessment
  As a homelab sysadmin
  I want to document risk level and mitigation for changes
  So that I can make informed decisions about proceeding

  Background:
    Given the Roundup tracker is running
    And I am logged in to the web UI as "admin"

  @story-3 @web-ui @smoke
  Scenario: Add risk assessment to change
    Given a change exists with title "Upgrade PostgreSQL" and status "planning"
    When I view the change details
    And I fill in the risk assessment:
      | Field      | Value                                              |
      | Impact     | Service downtime 1-2 hours during upgrade          |
      | Risk       | Database migration may fail on large datasets      |
    And I click "Submit"
    Then the change should have risk assessment saved
    And I should see impact "Service downtime 1-2 hours during upgrade"
    And I should see risk "Database migration may fail on large datasets"

  @story-3 @web-ui
  Scenario: Update risk assessment
    Given a change exists with title "Network reconfiguration" and status "planning"
    And the change has risk assessment "Low risk - simple configuration change"
    When I view the change details
    And I update the risk field to "Medium risk - requires service restart"
    And I click "Submit"
    Then the risk assessment should be updated
    And I should see risk "Medium risk - requires service restart"

  @story-3 @web-ui
  Scenario: View risk assessment on change details
    Given a change exists with title "Kernel upgrade" and status "planning"
    And the change has impact "System reboot required"
    And the change has risk "Boot failure possible if upgrade fails"
    When I view the change details
    Then I should see "Impact Assessment" section
    And I should see "System reboot required"
    And I should see "Risk Assessment" section
    And I should see "Boot failure possible if upgrade fails"

  @story-3 @web-ui
  Scenario: Risk assessment visible in change list
    Given the following changes exist:
      | title                | status   | risk                       |
      | Low risk change      | planning | Minimal impact expected    |
      | High risk change     | planning | Critical service downtime  |
      | Medium risk change   | planning | Requires careful execution |
    When I navigate to "Changes"
    Then I should see all 3 changes listed
    And the changes should show their risk assessments

  @story-3 @cli
  Scenario: Add risk assessment via CLI
    Given a change exists with ID "1"
    When I run "roundup-admin -i tracker set change1 impact='Service interruption possible' risk='Configuration rollback available'"
    Then the command should succeed
    And change "1" should have impact assessment
    And change "1" should have risk assessment

  @story-3 @cli
  Scenario: View risk assessment via CLI
    Given a change exists with ID "1"
    And the change has impact "Database downtime 30 minutes"
    And the change has risk "Backup and rollback plan in place"
    When I run "roundup-admin -i tracker get change1 impact risk"
    Then the command should succeed
    And the output should contain "Database downtime 30 minutes"
    And the output should contain "Backup and rollback plan in place"

  @story-3 @api
  Scenario: Create change with risk assessment via API
    When I POST "/api/change" with JSON:
      """
      {
        "title": "Storage migration",
        "description": "Migrate data to new SAN",
        "justification": "Current storage at capacity",
        "priority": "3",
        "category": "2",
        "status": "1",
        "impact": "Data unavailable during migration (4-6 hours)",
        "risk": "Data corruption risk - full backup completed"
      }
      """
    Then the response status should be 201
    And the created change should have impact assessment
    And the created change should have risk assessment

  @story-3 @api
  Scenario: Update risk assessment via API
    Given a change exists with ID "1"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "impact": "Updated impact: Service degradation during migration",
        "risk": "Updated risk: Gradual migration reduces risk"
      }
      """
    Then the response status should be 200
    And the change should have updated impact assessment
    And the change should have updated risk assessment

  @story-3 @api
  Scenario: Get change with risk assessment via API
    Given a change exists with ID "1"
    And the change has impact "Production service disruption"
    And the change has risk "Rollback procedure tested"
    When I GET "/api/change1"
    Then the response status should be 200
    And the response should include "impact"
    And the response should include "risk"
    And the impact should be "Production service disruption"
    And the risk should be "Rollback procedure tested"
