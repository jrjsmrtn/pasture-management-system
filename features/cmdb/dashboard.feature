# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@cmdb @story-7
Feature: CMDB Dashboard
  As a homelab sysadmin
  I want a dashboard view of my CMDB health
  So that I can understand my infrastructure at a glance

  @web-ui @smoke
  Scenario: View CMDB dashboard
    Given I am logged in to the web UI
    When I navigate to "Dashboard"
    Then I should see "CMDB Dashboard"
    And I should see "Total CIs"
    And I should see "By Type"
    And I should see "By Criticality"
    And I should see "By Status"
    And I should see "Relationships"
    And I should see "Issues & Changes"

  @web-ui
  Scenario: Dashboard displays CI statistics
    Given the following CIs exist:
      | name          | type           | status | criticality |
      | db-server-01  | Server         | Active | High        |
      | db-server-02  | Server         | Active | Medium      |
      | core-switch   | Network Device | Active | High        |
    And I am logged in to the web UI
    When I navigate to "Dashboard"
    Then I should see "Total CIs"
    And I should see "3" in the Total CIs stat
    And I should see "Servers" in the dashboard
    And I should see "Network Devices" in the dashboard

  @web-ui
  Scenario: Dashboard shows CI breakdowns by type
    Given the following CIs exist:
      | name           | type           | status |
      | web-server-01  | Server         | Active |
      | web-server-02  | Server         | Active |
      | app-server-01  | Server         | Active |
      | core-switch-01 | Network Device | Active |
      | nas-01         | Storage        | Active |
    And I am logged in to the web UI
    When I navigate to "Dashboard"
    Then the "Servers" count should be "3"
    And the "Network Devices" count should be "1"
    And the "Storage" count should be "1"

  @web-ui
  Scenario: Dashboard shows CI breakdowns by criticality
    Given the following CIs exist:
      | name         | type   | status | criticality |
      | critical-db  | Server | Active | Very High   |
      | prod-web     | Server | Active | High        |
      | dev-server   | Server | Active | Low         |
    And I am logged in to the web UI
    When I navigate to "Dashboard"
    Then the "Very High" criticality count should be "1"
    And the "High" criticality count should be "1"
    And the "Low" criticality count should be "1"
