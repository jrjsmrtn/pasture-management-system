# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Create Issue via CLI
  As a homelab sysadmin
  I want to create issues from the command line
  So that I can quickly report issues during troubleshooting

  Background:
    Given the Roundup tracker database is accessible

  @smoke
  Scenario: Create issue via command line with all fields
    When I run the CLI command to create an issue with:
      | field    | value                          |
      | title    | Network connectivity issue     |
      | priority | urgent                         |
    Then the CLI command should succeed
    And the command should return an issue ID
    And the issue should exist in the database
    And the issue title should be "Network connectivity issue"
    And the issue priority should be "urgent"

  @smoke
  Scenario: Create issue with minimal fields
    When I run the CLI command to create an issue with:
      | field | value                    |
      | title | Minimal test issue       |
    Then the CLI command should succeed
    And the command should return an issue ID
    And the issue should exist in the database
    And the issue title should be "Minimal test issue"
    And the issue should have default priority
