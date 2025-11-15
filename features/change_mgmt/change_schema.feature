# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-3
Feature: Change Request Schema
  As a homelab sysadmin
  I want change requests to have a defined schema
  So that I can track planned infrastructure changes systematically

  Background:
    Given the Roundup tracker is running at "http://localhost:8080/pms"

  @api
  Scenario: Verify change schema fields via API
    Given I have a valid API token
    When I GET "/rest/data/change" via API
    Then the response status should be 200
    And the response should contain collection "data"

  @api
  Scenario: Verify change priorities exist
    Given I have a valid API token
    When I GET "/rest/data/changepriority" via API
    Then the response status should be 200
    And the response should contain changepriority "low"
    And the response should contain changepriority "medium"
    And the response should contain changepriority "high"
    And the response should contain changepriority "critical"

  @api
  Scenario: Verify change categories exist
    Given I have a valid API token
    When I GET "/rest/data/changecategory" via API
    Then the response status should be 200
    And the response should contain changecategory "software"
    And the response should contain changecategory "hardware"
    And the response should contain changecategory "configuration"
    And the response should contain changecategory "network"

  @api
  Scenario: Verify change statuses exist
    Given I have a valid API token
    When I GET "/rest/data/changestatus" via API
    Then the response status should be 200
    And the response should contain changestatus "proposed"
    And the response should contain changestatus "approved"
    And the response should contain changestatus "scheduled"
    And the response should contain changestatus "implemented"
    And the response should contain changestatus "closed"
