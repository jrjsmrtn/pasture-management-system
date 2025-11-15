# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Create Issue via Web UI
  As a homelab sysadmin
  I want to create issues through the web interface
  So that I can track problems in my homelab

  Background:
    Given the Roundup tracker is running
    And I am logged in to the web UI as "admin"

  @smoke @web-ui
  Scenario: Create issue with required fields
    When I navigate to the "New Issue" page
    And I enter the following issue details:
      | field       | value                                    |
      | title       | Server backup failure                    |
      | priority    | urgent                                   |
    And I submit the issue
    Then I should see a success message
    And the issue should appear in the issue list
    And the issue title should be "Server backup failure"
    And the issue priority should be "urgent"

  @validation @web-ui
  Scenario: Cannot create issue without title
    When I navigate to the "New Issue" page
    And I submit the issue without entering a title
    Then I should see a validation error
    And the issue should not be created
