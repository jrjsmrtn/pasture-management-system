# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@cmdb @story-5
Feature: CI Search and Filtering
  As a homelab sysadmin
  I want to search and filter configuration items
  So that I can quickly find infrastructure components

  @web-ui @smoke
  Scenario: Search CIs by name
    Given the following CIs exist:
      | name           | type   |
      | db-server-01   | Server |
      | db-server-02   | Server |
      | web-server-01  | Server |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I search for "db-server"
    Then I should see 2 CIs in the results
    And I should see CI "db-server-01"
    And I should see CI "db-server-02"
    And I should not see CI "web-server-01"

  @web-ui
  Scenario: Filter CIs by type
    Given the following CIs exist:
      | name           | type           |
      | db-server-01   | Server         |
      | app-server-01  | Server         |
      | core-switch-01 | Network Device |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I filter by type "Server"
    Then I should see 2 CIs in the results
    And I should see CI "db-server-01"
    And I should see CI "app-server-01"
    And I should not see CI "core-switch-01"

  @web-ui
  Scenario: Filter CIs by criticality
    Given the following CIs exist:
      | name           | type   | criticality |
      | db-server-01   | Server | High        |
      | app-server-01  | Server | Medium      |
      | test-server-01 | Server | Low         |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I filter by criticality "High"
    Then I should see 1 CI in the results
    And I should see CI "db-server-01"
    And I should not see CI "app-server-01"

  @web-ui
  Scenario: Combine type and criticality filters
    Given the following CIs exist:
      | name           | type           | criticality |
      | db-server-01   | Server         | High        |
      | app-server-01  | Server         | Medium      |
      | core-switch-01 | Network Device | High        |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I filter by type "Server"
    And I filter by criticality "High"
    Then I should see 1 CI in the results
    And I should see CI "db-server-01"

  @web-ui
  Scenario: Filter CIs by status
    Given the following CIs exist:
      | name          | type   | status  |
      | db-server-01  | Server | Active  |
      | old-server-01 | Server | Retired |
      | app-server-01 | Server | Active  |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I filter CIs by status "Active"
    Then I should see 2 CIs in the results
    And I should see CI "db-server-01"
    And I should see CI "app-server-01"
    And I should not see CI "old-server-01"

  @web-ui
  Scenario: Use quick filter for active servers
    Given the following CIs exist:
      | name          | type   | status  |
      | db-server-01  | Server | Active  |
      | old-server-01 | Server | Retired |
      | app-server-01 | Server | Active  |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I click quick filter "Active Servers"
    Then I should see 2 CIs in the results
    And I should see CI "db-server-01"
    And I should see CI "app-server-01"

  @web-ui
  Scenario: Search by location
    Given the following CIs exist:
      | name           | type   | location      |
      | db-server-01   | Server | Rack 1        |
      | db-server-02   | Server | Rack 1        |
      | web-server-01  | Server | Rack 2        |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I search for "Rack 1"
    Then I should see 2 CIs in the results
    And I should see CI "db-server-01"
    And I should see CI "db-server-02"

  @web-ui
  Scenario: Sort CIs by name
    Given the following CIs exist:
      | name           | type   |
      | zulu-server    | Server |
      | alpha-server   | Server |
      | bravo-server   | Server |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I sort by "Name" ascending
    Then the CIs should be displayed in order:
      | alpha-server  |
      | bravo-server  |
      | zulu-server   |

  @web-ui
  Scenario: Sort CIs by criticality
    Given the following CIs exist:
      | name           | type   | criticality |
      | server-a       | Server | Low         |
      | server-b       | Server | High        |
      | server-c       | Server | Medium      |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I sort by "Criticality" descending
    Then the CIs should be displayed in order:
      | server-b |
      | server-c |
      | server-a |

  @web-ui
  Scenario: Clear all filters
    Given the following CIs exist:
      | name           | type   | status |
      | db-server-01   | Server | Active |
      | app-server-01  | Server | Active |
      | old-server-01  | Server | Retired |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I filter CIs by status "Active"
    Then I should see 2 CIs in the results
    When I click "Clear Filters"
    Then I should see 3 CIs in the results

  @api
  Scenario: Export CMDB to JSON via API
    Given the following CIs exist:
      | name           | type   | status |
      | db-server-01   | Server | Active |
      | app-server-01  | Server | Active |
    And I have a valid API token
    When I GET "/api/cmdb/export?format=json"
    Then the response status should be 200
    And the response should be valid JSON
    And the response should include CI "db-server-01"
    And the response should include CI "app-server-01"

  @web-ui
  Scenario: Export CMDB to CSV
    Given the following CIs exist:
      | name           | type   | status |
      | db-server-01   | Server | Active |
      | app-server-01  | Server | Active |
    And I am logged in to the web UI
    When I navigate to "CMDB"
    And I click "Export to CSV"
    Then a CSV file should be downloaded
    And the CSV should contain "db-server-01"
    And the CSV should contain "app-server-01"
