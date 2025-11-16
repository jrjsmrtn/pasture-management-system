# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-1 @cmdb
Feature: Configuration Item Schema
  As a homelab sysadmin
  I want to track configuration items in my infrastructure
  So that I can maintain an inventory of my homelab assets

  Background:
    Given I am logged in to the web UI

  @api
  Scenario: Verify CI schema structure
    Given I have a valid API token
    When I GET "/api/schema/ci"
    Then the response should include base fields:
      | field       | type   | required |
      | name        | string | true     |
      | type        | string | true     |
      | status      | string | true     |
      | location    | string | false    |
      | owner       | string | false    |
      | criticality | string | false    |
    And the response should include CI types:
      | type            |
      | Server          |
      | Network Device  |
      | Storage         |
      | Software        |
      | Service         |
      | Virtual Machine |

  @api
  Scenario: Verify server-specific attributes
    Given I have a valid API token
    When I GET "/api/schema/ci/server"
    Then the response should include server-specific fields:
      | field      | type   |
      | cpu_cores  | number |
      | ram_gb     | number |
      | os         | string |
      | ip_address | string |
