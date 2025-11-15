# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Create Issue via API
  As an automation script
  I want to create issues via REST API
  So that I can integrate issue tracking with monitoring tools

  Background:
    Given the Roundup REST API is accessible

  @smoke
  Scenario: Create issue via REST API
    Given I have a valid API credential
    When I POST to the API with:
      | field    | value                        |
      | title    | Database connection timeout  |
      | priority | urgent                       |
    Then the API response status should be 201 or 200
    And the response should contain an issue ID
    And the issue should exist in the database
    And the issue title should be "Database connection timeout"
    And the issue priority should be "urgent"

  @security
  Scenario: Cannot create issue without authentication
    When I POST to the API without authentication with:
      | field | value         |
      | title | Unauthorized  |
    Then the API response status should be 403 or 401
    And the issue should not be created via API
