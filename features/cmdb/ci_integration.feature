# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@cmdb @story-4
Feature: Link CIs to Issues and Changes
  As a homelab sysadmin
  I want to link issues and changes to affected CIs
  So that I can track which infrastructure is impacted

  @web-ui @smoke
  Scenario: Link issue to affected CI
    Given an issue exists with title "Database connection failures"
    And a CI exists with name "db-server-01" and type "Server"
    And I am logged in to the web UI
    When I view the issue
    And I select affected CI "db-server-01"
    And I click "Submit Changes"
    Then the issue should be linked to "db-server-01"
    And I should see "db-server-01" in the affected CIs section

  @web-ui
  Scenario: View CI with related issues and changes
    Given a CI exists with name "db-server-01" and type "Server"
    And 2 issues are linked to "db-server-01"
    And 1 change is linked to "db-server-01"
    And I am logged in to the web UI
    When I view CI "db-server-01"
    Then I should see "Related Issues" section with 2 items
    And I should see "Related Changes" section with 1 item

  @web-ui @validation
  Scenario: Impact analysis for high-criticality CI
    Given a CI exists with name "core-switch-01" and type "Network Device"
    And CI "core-switch-01" has criticality "Very High"
    And a change exists with title "Firmware upgrade"
    And I am logged in to the web UI
    When I edit the change
    And I select target CI "core-switch-01"
    And I click "Submit"
    Then I should see "WARNING: This change affects a very high criticality component"
    And the change should be linked to "core-switch-01"

  @web-ui
  Scenario: Link change to multiple CIs
    Given a CI exists with name "web-server-01" and type "Server"
    And a CI exists with name "app-server-01" and type "Server"
    And a change exists with title "Security patches"
    And I am logged in to the web UI
    When I edit the change
    And I select target CI "web-server-01"
    And I select target CI "app-server-01"
    And I click "Submit"
    Then the change should be linked to "web-server-01"
    And the change should be linked to "app-server-01"

  @api
  Scenario: Create change with CI targets via API
    Given a CI exists with name "db-server-01" and type "Server"
    And I have a valid API token
    When I POST to "/api/change" with JSON:
      """
      {
        "title": "Upgrade database server",
        "description": "Upgrade to latest version",
        "justification": "Security patches",
        "priority": "3",
        "category": "2",
        "target_cis": ["db-server-01"]
      }
      """
    Then the response status should be 201
    And the change should be linked to CI "db-server-01"

  @cli
  Scenario: Create issue with affected CI via CLI
    Given a CI exists with name "storage-01" and type "Storage"
    When I run "roundup-admin -i tracker create issue title='Storage full' affected_cis=storage-01"
    Then the command should succeed
    And the issue should be linked to CI "storage-01"

  @web-ui
  Scenario: View impact of CI relationships on change
    Given a CI "web-service" depends on "app-vm-01"
    And CI "app-vm-01" runs on "db-server-01"
    And a change exists with title "Server maintenance"
    And I am logged in to the web UI
    When I edit the change
    And I select target CI "db-server-01"
    And I click "Submit"
    Then I should see "Impact: This CI supports 1 dependent CI"
    And I should see "app-vm-01" in the dependent CIs list

  @api
  Scenario: Get CIs linked to an issue via API
    Given an issue exists with title "Network timeout"
    And a CI "core-switch-01" is linked to the issue
    And a CI "backup-switch-01" is linked to the issue
    And I have a valid API token
    When I GET "/api/issue/1/cis"
    Then the response status should be 200
    And the response should contain 2 CIs
    And the response should include "core-switch-01"
    And the response should include "backup-switch-01"
