# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: View Issue List
  As a homelab sysadmin
  I want to see all my issues in a list
  So that I can track what needs attention

  Background:
    Given the Roundup tracker is running

  @smoke
  Scenario: View list of issues
    Given I am logged in to the web UI as "admin"
    And the following issues exist:
      | title                      | priority |
      | Network connectivity issue | urgent   |
      | Database backup failed     | critical |
      | Disk space warning         | bug      |
    When I navigate to the "Issues" page
    Then I should see 3 issues in the list
    And I should see issue "Network connectivity issue"
    And I should see issue "Database backup failed"
    And I should see issue "Disk space warning"

  @smoke
  Scenario: View issue details
    Given I am logged in to the web UI as "admin"
    And an issue exists with title "Test Issue Details"
    When I navigate to the "Issues" page
    And I click on the issue "Test Issue Details"
    Then I should be on the issue details page
    And I should see the issue title "Test Issue Details"
