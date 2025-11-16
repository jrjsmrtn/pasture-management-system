# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

@story-2 @cmdb
Feature: Create Configuration Items
  As a homelab sysadmin
  I want to add configuration items to my CMDB
  So that I can track what infrastructure I have

  Background:
    Given I am logged in to the web UI

  @web-ui @smoke
  Scenario: Create server CI
    When I navigate to "CMDB"
    And I click "New Configuration Item"
    And I select type "Server"
    And I enter name "db-server-01"
    And I select status "Active"
    And I enter location "Rack 1, Unit 5"
    And I select criticality "High"
    And I enter CPU cores "8"
    And I enter RAM GB "32"
    And I enter OS "Ubuntu 24.04 LTS"
    And I enter IP address "192.168.1.50"
    And I click "Submit"
    Then I should see "Configuration item created successfully"
    And the CI should appear in the CMDB

  @web-ui @validation
  Scenario: Cannot create CI without name
    When I navigate to "CMDB"
    And I click "New Configuration Item"
    And I select type "Server"
    And I click "Submit"
    Then I should see "Name is required"

  @web-ui
  Scenario: Create network device CI
    When I navigate to "CMDB"
    And I click "New Configuration Item"
    And I select type "Network Device"
    And I enter name "core-switch-01"
    And I select status "Active"
    And I enter location "Network closet"
    And I select criticality "Very High"
    And I enter IP address "192.168.1.1"
    And I enter ports "48"
    And I click "Submit"
    Then I should see "Configuration item created successfully"
    And the CI "core-switch-01" should exist

  @web-ui
  Scenario: Create storage CI
    When I navigate to "CMDB"
    And I click "New Configuration Item"
    And I select type "Storage"
    And I enter name "nas-01"
    And I select status "Active"
    And I enter location "Server room"
    And I enter capacity GB "8000"
    And I click "Submit"
    Then I should see "Configuration item created successfully"

  @web-ui
  Scenario: Create virtual machine CI
    When I navigate to "CMDB"
    And I click "New Configuration Item"
    And I select type "Virtual Machine"
    And I enter name "app-vm-01"
    And I select status "Active"
    And I select criticality "Medium"
    And I enter CPU cores "4"
    And I enter RAM GB "16"
    And I enter OS "Debian 12"
    And I click "Submit"
    Then I should see "Configuration item created successfully"

  @cli
  Scenario: Create network device via CLI
    When I run "roundup-admin -i tracker create ci name=core-switch-01 type=2 status=5 location='Network closet' ip_address=192.168.1.1 ports=48"
    Then the command should succeed
    And the output should contain "1"

  @cli
  Scenario: Create server via CLI
    When I run "roundup-admin -i tracker create ci name=web-server-01 type=1 status=5 cpu_cores=4 ram_gb=16 os='Rocky Linux 9'"
    Then the command should succeed

  @api
  Scenario: Create virtual machine via API
    Given I have a valid API token
    When I POST to "/api/cmdb/ci" with JSON:
      """
      {
        "name": "app-vm-01",
        "type": "6",
        "status": "5",
        "location": "Proxmox Cluster",
        "criticality": "3",
        "cpu_cores": 4,
        "ram_gb": 16,
        "os": "Debian 12"
      }
      """
    Then the response status should be 201
    And the CI should exist in the database
