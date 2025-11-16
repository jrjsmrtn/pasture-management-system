# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Link Changes to Issues
  As a homelab sysadmin
  I want to link change requests to related issues
  So that I can track which changes address which problems

  Background:
    Given the Roundup tracker is running
    And I am logged in to the web UI as "admin"

  @story-2 @web-ui @smoke
  Scenario: Link change to existing issue
    Given an issue exists with title "Database performance slow"
    And a change exists with title "Upgrade database"
    When I view the change details
    And I add related issue "Database performance slow"
    And I click "Submit"
    Then I should see "Database performance slow" in related issues
    And the change should be linked to the issue

  @story-2 @web-ui
  Scenario: View linked changes from issue
    Given an issue exists with title "Network connectivity problem"
    And a change "Network reconfiguration" is linked to the issue
    And a change "Router firmware update" is linked to the issue
    When I view the issue details
    Then I should see "Related Changes" section
    And I should see 2 linked changes
    And I should see "Network reconfiguration"
    And I should see "Router firmware update"

  @story-2 @web-ui
  Scenario: Remove issue link from change
    Given an issue exists with title "Disk space warning"
    And a change exists with title "Add storage capacity"
    And the change is linked to the issue
    When I view the change details
    And I remove the related issue "Disk space warning"
    And I click "Submit"
    Then I should not see "Disk space warning" in related issues
    And the change should not be linked to the issue

  @story-2 @web-ui
  Scenario: Link multiple issues to one change
    Given the following issues exist:
      | title                    |
      | CPU overheating          |
      | Server thermal shutdown  |
    And a change exists with title "Install new cooling system"
    When I view the change details
    And I add related issue "CPU overheating"
    And I add related issue "Server thermal shutdown"
    And I click "Submit"
    Then I should see 2 related issues
    And I should see "CPU overheating"
    And I should see "Server thermal shutdown"

  @story-2 @cli
  Scenario: Link change to issue via CLI
    Given a change exists with ID "1"
    And an issue exists with ID "1"
    When I run "roundup-admin -i tracker set change1 related_issues=1"
    Then the command should succeed
    And change "1" should be linked to issue "1"

  @story-2 @cli
  Scenario: Link multiple issues to change via CLI
    Given a change exists with ID "1"
    And the following issues exist with IDs "1,2,3"
    When I run "roundup-admin -i tracker set change1 related_issues=1,2,3"
    Then the command should succeed
    And change "1" should be linked to 3 issues

  @story-2 @api
  Scenario: Create change with issue links via API
    Given an issue exists with ID "1"
    When I POST "/api/change" with JSON:
      """
      {
        "title": "Fix network issue",
        "description": "Reconfigure network settings",
        "justification": "Resolve connectivity problems",
        "priority": "2",
        "category": "4",
        "status": "1",
        "related_issues": ["1"]
      }
      """
    Then the response status should be 201
    And the created change should be linked to issue "1"

  @story-2 @api
  Scenario: Update change to add issue link via API
    Given a change exists with ID "1"
    And an issue exists with ID "2"
    When I PATCH "/api/change1" with JSON:
      """
      {
        "related_issues": ["2"]
      }
      """
    Then the response status should be 200
    And change "1" should be linked to issue "2"

  @story-2 @api
  Scenario: Get change with issue links via API
    Given an issue exists with ID "1" and title "Test issue"
    And a change exists with ID "1"
    And the change is linked to issue "1"
    When I GET "/api/change1"
    Then the response status should be 200
    And the response should include related_issues
    And the related_issues should contain issue "1"
