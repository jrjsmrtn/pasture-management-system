# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-3 @cmdb
Feature: CI Relationships and Dependencies
  As a homelab sysadmin
  I want to define relationships between configuration items
  So that I can understand dependencies in my infrastructure

  Background:
    Given I am logged in to the web UI

  @web-ui
  Scenario: Link virtual machine to physical server
    Given a CI exists with name "db-server-01" and type "Server"
    And a CI exists with name "app-vm-01" and type "Virtual Machine"
    When I view CI "app-vm-01"
    And I click "Add Relationship"
    And I select relationship type "Runs On"
    And I select target CI "db-server-01"
    And I click "Save"
    Then "app-vm-01" should have relationship "Runs On" to "db-server-01"
    And "db-server-01" should have relationship "Hosts" to "app-vm-01"

  @web-ui
  Scenario: View CI dependency tree
    Given a CI "web-service" depends on "app-vm-01"
    And CI "app-vm-01" runs on "db-server-01"
    When I view CI "web-service"
    And I click "View Dependencies"
    Then I should see dependency tree:
      """
      web-service
        └─ Depends On: app-vm-01
           └─ Runs On: db-server-01
      """

  @web-ui @validation
  Scenario: Prevent circular dependency
    Given a CI "ci-a" depends on "ci-b"
    And a CI "ci-b" depends on "ci-c"
    When I view CI "ci-c"
    And I try to add dependency to "ci-a"
    Then I should see "Circular dependency detected"
    And the relationship should not be created

  @web-ui
  Scenario: View all relationships for a CI
    Given a CI exists with name "app-server-01" and type "Server"
    And CI "app-server-01" has relationship "Hosts" to "web-vm-01"
    And CI "app-server-01" has relationship "Hosts" to "db-vm-01"
    And CI "app-server-01" has relationship "Connects To" to "core-switch-01"
    When I view CI "app-server-01"
    Then I should see 3 relationships
    And I should see relationship "Hosts" to "web-vm-01"
    And I should see relationship "Hosts" to "db-vm-01"
    And I should see relationship "Connects To" to "core-switch-01"

  @web-ui
  Scenario: Remove CI relationship
    Given a CI "vm-01" runs on "server-01"
    When I view CI "vm-01"
    And I click "Remove" on relationship to "server-01"
    And I confirm removal
    Then "vm-01" should have no relationships
    And "server-01" should have no relationships

  @api
  Scenario: Create CI relationship via API
    Given I have a valid API token
    And a CI exists with ID "1" and type "Server"
    And a CI exists with ID "2" and type "Virtual Machine"
    When I POST to "/api/cmdb/relationships" with JSON:
      """
      {
        "source_ci": "2",
        "relationship_type": "1",
        "target_ci": "1"
      }
      """
    Then the response status should be 201
    And the relationship should exist

  @api
  Scenario: Query CI relationships via API
    Given I have a valid API token
    And a CI exists with ID "5"
    And CI "5" has 2 relationships
    When I GET "/api/cmdb/ci/5/relationships"
    Then the response status should be 200
    And the response should contain 2 relationships
