# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-2
Feature: Assign Issues to Owner
  As a homelab sysadmin
  I want to assign issues to specific people
  So that responsibilities are clear

  Background:
    Given the Roundup tracker is running at "http://localhost:8080/pms"

  @web-ui @smoke
  Scenario: Assign issue to user during creation
    Given I am logged in to the web UI as "admin" with password "admin"
    And an issue exists with title "Database backup script failing" and is unassigned
    When I view the issue details
    And I assign the issue to user "admin"
    And I submit the issue
    Then the issue should be assigned to "admin"

  @web-ui
  Scenario: Change issue assignee
    Given I am logged in to the web UI as "admin" with password "admin"
    And an issue exists with title "Server monitoring alerts" and is unassigned
    When I view the issue details
    And I assign the issue to user "admin"
    And I submit the issue
    Then the issue should be assigned to "admin"

  @web-ui
  Scenario: Filter issues by assignee
    Given I am logged in to the web UI as "admin" with password "admin"
    And the following issues exist:
      | title                    | priority | assignedto |
      | Network switch failure   | critical | admin      |
      | Update documentation     | bug      |            |
      | Backup disk full         | urgent   | admin      |
    When I navigate to the "Issues" page
    And I filter issues by assignee "admin"
    Then I should see 2 issues in the list
    And I should see issue "Network switch failure"
    And I should see issue "Backup disk full"
    And I should not see issue "Update documentation"

  @web-ui
  Scenario: View unassigned issues
    Given I am logged in to the web UI as "admin" with password "admin"
    And the following issues exist:
      | title                  | priority | assignedto |
      | Fix firewall rules     | critical | admin      |
      | Review security audit  | bug      |            |
      | Clean up old backups   | bug      |            |
    When I navigate to the "Issues" page
    And I filter issues by assignee "(unassigned)"
    Then I should see 2 issues in the list
    And I should see issue "Review security audit"
    And I should see issue "Clean up old backups"
    And I should not see issue "Fix firewall rules"
