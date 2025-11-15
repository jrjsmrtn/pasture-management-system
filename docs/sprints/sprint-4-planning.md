<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 4 Plan - Pasture Management System

**Sprint Duration**: 2 weeks
**Sprint Goal**: Implement Configuration Management Database (CMDB) foundation
**Target Version**: v0.5.0
**Start Date**: TBD
**End Date**: TBD

## Sprint Objective

Establish the CMDB capability for tracking homelab infrastructure configuration items (CIs), their attributes, and relationships. Integrate CMDB with issues and changes to demonstrate ITIL-inspired service management. This sprint completes the core ITIL trilogy: Incident, Change, and Configuration Management.

## User Stories

### Epic: CMDB Foundation

#### Story 1: Define Configuration Item Schema
**As a** homelab sysadmin
**I want** to track configuration items in my infrastructure
**So that** I can maintain an inventory of my homelab assets

**Acceptance Criteria**:
- CI types: Server, Network Device, Storage, Software, Service, Virtual Machine
- Common attributes: name, type, status, location, owner, criticality
- Type-specific attributes (e.g., servers have CPU/RAM, network devices have IP/ports)
- CI lifecycle states: Planning, Ordered, In Stock, Deployed, Active, Maintenance, Retired
- Schema documented in reference docs

**BDD Scenarios**: (Feature file: `features/cmdb/ci_schema.feature`)
```gherkin
@story-1 @api
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
    | type           |
    | Server         |
    | Network Device |
    | Storage        |
    | Software       |
    | Service        |
    | Virtual Machine|

@story-1 @api
Scenario: Verify server-specific attributes
  When I GET "/api/schema/ci/server"
  Then the response should include server-specific fields:
    | field      | type   |
    | cpu_cores  | number |
    | ram_gb     | number |
    | os         | string |
    | ip_address | string |
```

**Story Points**: 5

---

#### Story 2: Create Configuration Items
**As a** homelab sysadmin
**I want** to add configuration items to my CMDB
**So that** I can track what infrastructure I have

**Acceptance Criteria**:
- Web UI form for CI creation
- Type-specific attribute forms
- CI saved to database
- Success confirmation displayed
- CI viewable in CI list

**BDD Scenarios**: (Feature file: `features/cmdb/create_ci.feature`)
```gherkin
@story-2 @web-ui @smoke
Scenario: Create server CI
  Given I am logged in to the web UI
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

@story-2 @web-ui @validation
Scenario: Cannot create CI without name
  Given I am logged in to the web UI
  When I navigate to "CMDB"
  And I click "New Configuration Item"
  And I select type "Server"
  And I click "Submit"
  Then I should see "Name is required"

@story-2 @cli
Scenario: Create network device via CLI
  When I run "roundup-client create ci type=network_device name=core-switch-01 status=active location='Network closet' ip_address=192.168.1.1 ports=48"
  Then the command should succeed
  And I should see "CI created: #1"

@story-2 @api
Scenario: Create virtual machine via API
  Given I have a valid API token
  When I POST to "/api/cmdb/ci" with JSON:
    """
    {
      "type": "virtual_machine",
      "name": "app-vm-01",
      "status": "active",
      "location": "Proxmox Cluster",
      "criticality": "medium",
      "cpu_cores": 4,
      "ram_gb": 16,
      "os": "Debian 12"
    }
    """
  Then the response status should be 201
  And the CI should exist in the database
```

**Story Points**: 5

---

#### Story 3: CI Relationships and Dependencies
**As a** homelab sysadmin
**I want** to define relationships between configuration items
**So that** I can understand dependencies in my infrastructure

**Acceptance Criteria**:
- Relationship types: Runs On, Depends On, Connects To, Contains, Hosted By
- Bidirectional relationships (e.g., VM "Runs On" Server, Server "Hosts" VM)
- Multiple relationships per CI
- Relationship visualization in UI
- Circular dependency detection

**BDD Scenarios**: (Feature file: `features/cmdb/ci_relationships.feature`)
```gherkin
@story-3 @web-ui
Scenario: Link virtual machine to physical server
  Given a CI exists with name "db-server-01" and type "Server"
  And a CI exists with name "app-vm-01" and type "Virtual Machine"
  When I view CI "app-vm-01"
  And I click "Add Relationship"
  And I select relationship type "Runs On"
  And I select CI "db-server-01"
  And I click "Save"
  Then "app-vm-01" should have relationship "Runs On" to "db-server-01"
  And "db-server-01" should have relationship "Hosts" to "app-vm-01"

@story-3 @web-ui
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

@story-3 @web-ui @validation
Scenario: Prevent circular dependency
  Given a CI "ci-a" depends on "ci-b"
  And a CI "ci-b" depends on "ci-c"
  When I view CI "ci-c"
  And I try to add dependency to "ci-a"
  Then I should see "Circular dependency detected"
  And the relationship should not be created

@story-3 @api
Scenario: Create CI relationship via API
  Given a CI exists with ID "1" (server)
  And a CI exists with ID "2" (VM)
  When I POST to "/api/cmdb/relationships" with JSON:
    """
    {
      "source_ci": 2,
      "relationship_type": "runs_on",
      "target_ci": 1
    }
    """
  Then the response status should be 201
  And the relationship should exist
```

**Story Points**: 8

---

#### Story 4: Link CIs to Issues and Changes
**As a** homelab sysadmin
**I want** to link issues and changes to affected CIs
**So that** I can track which infrastructure is impacted

**Acceptance Criteria**:
- Issue can reference affected CIs
- Change can reference target CIs
- CI view shows related issues and changes
- Impact analysis based on CI criticality
- Filter issues/changes by CI

**BDD Scenarios**: (Feature file: `features/cmdb/ci_integration.feature`)
```gherkin
@story-4 @web-ui
Scenario: Link issue to affected CI
  Given an issue exists with title "Database connection failures"
  And a CI exists with name "db-server-01"
  When I view the issue details
  And I click "Link CI"
  And I select CI "db-server-01"
  And I click "Add"
  Then the issue should be linked to "db-server-01"
  And I should see "Affected CI: db-server-01"

@story-4 @web-ui
Scenario: View CI issues and changes
  Given a CI exists with name "db-server-01"
  And 2 issues are linked to "db-server-01"
  And 1 change is linked to "db-server-01"
  When I view CI "db-server-01"
  Then I should see "Related Issues" section with 2 issues
  And I should see "Related Changes" section with 1 change

@story-4 @web-ui
Scenario: Impact analysis for high-criticality CI
  Given a CI exists with name "core-switch-01" and criticality "High"
  And a change exists with title "Firmware upgrade"
  When I link change to "core-switch-01"
  Then I should see "WARNING: This change affects a high-criticality component"
  And I should see "Impact: Network connectivity for entire lab"

@story-4 @api
Scenario: Create change with CI targets via API
  Given a CI exists with ID "5"
  When I POST to "/api/changes" with JSON:
    """
    {
      "title": "Upgrade database server",
      "description": "Upgrade to latest version",
      "justification": "Security patches",
      "priority": "high",
      "category": "software",
      "target_cis": [5]
    }
    """
  Then the response status should be 201
  And the change should be linked to CI "5"
```

**Story Points**: 5

---

#### Story 5: CI Search and Filtering
**As a** homelab sysadmin
**I want** to search and filter configuration items
**So that** I can quickly find infrastructure components

**Acceptance Criteria**:
- Search by name, type, location, status
- Filter by criticality, owner, CI type
- Sort by various attributes
- Export CMDB to CSV/JSON
- Quick filters for common searches

**BDD Scenarios**: (Feature file: `features/cmdb/ci_search.feature`)
```gherkin
@story-5 @web-ui
Scenario: Search CIs by name
  Given the following CIs exist:
    | name           | type   |
    | db-server-01   | Server |
    | db-server-02   | Server |
    | web-server-01  | Server |
  When I navigate to "CMDB"
  And I search for "db-server"
  Then I should see 2 CIs
  And I should see "db-server-01" and "db-server-02"

@story-5 @web-ui
Scenario: Filter CIs by type and criticality
  Given the following CIs exist:
    | name           | type   | criticality |
    | db-server-01   | Server | High        |
    | app-server-01  | Server | Medium      |
    | core-switch-01 | Network| High        |
  When I navigate to "CMDB"
  And I filter by type "Server"
  And I filter by criticality "High"
  Then I should see 1 CI
  And I should see "db-server-01"

@story-5 @web-ui
Scenario: View all active servers
  Given the following CIs exist:
    | name          | type   | status |
    | db-server-01  | Server | Active |
    | old-server-01 | Server | Retired|
    | app-server-01 | Server | Active |
  When I navigate to "CMDB"
  And I click quick filter "Active Servers"
  Then I should see 2 CIs

@story-5 @api
Scenario: Export CMDB via API
  Given I have a valid API token
  When I GET "/api/cmdb/export?format=json"
  Then the response status should be 200
  And the response should be valid JSON
  And the response should include all CIs
```

**Story Points**: 5

---

## Technical Tasks

### CMDB Schema
- [ ] Design CI base schema and type-specific schemas
- [ ] Create database migrations
- [ ] Implement CI type inheritance/composition
- [ ] Add lifecycle state management

### CI Management
- [ ] Implement CI creation (web/CLI/API)
- [ ] Create CI list and detail views
- [ ] Add type-specific attribute forms
- [ ] Implement CI search and filtering

### Relationships
- [ ] Design relationship schema
- [ ] Implement relationship management
- [ ] Add relationship visualization
- [ ] Implement circular dependency detection
- [ ] Create dependency tree views

### Integration
- [ ] Link CIs to issues
- [ ] Link CIs to changes
- [ ] Implement impact analysis
- [ ] Add CI context to issue/change views

### Documentation
- [ ] Tutorial: "Building Your Homelab CMDB"
- [ ] How-to: "Documenting Infrastructure Dependencies"
- [ ] Reference: "CMDB Schema and Attributes"
- [ ] Reference: "CI Relationship Types"
- [ ] Explanation: "Why Configuration Management Matters"

## Definition of Done

- [ ] All user stories completed with acceptance criteria met
- [ ] All BDD scenarios implemented and passing
- [ ] CMDB functional with CIs and relationships
- [ ] CI-Issue-Change integration working
- [ ] Search and filtering operational
- [ ] Code passes pre-commit hooks
- [ ] Documentation completed
- [ ] Test coverage >85%
- [ ] CHANGELOG.md updated for v0.5.0
- [ ] Sprint retrospective completed

## Sprint Backlog

| Task | Story Points | Status |
|------|-------------|--------|
| Story 1: Define CI Schema | 5 | Not Started |
| Story 2: Create Configuration Items | 5 | Not Started |
| Story 3: CI Relationships | 8 | Not Started |
| Story 4: Link CIs to Issues/Changes | 5 | Not Started |
| Story 5: CI Search and Filtering | 5 | Not Started |
| Documentation Tasks | 5 | Not Started |

**Total Story Points**: 33

## Risks and Dependencies

### Risks
- **Schema Complexity**: Type-specific attributes may be complex to model
  - *Mitigation*: Start with common attributes, add type-specific incrementally
- **Relationship Complexity**: Dependency management can be intricate
  - *Mitigation*: Implement basic relationships first, add advanced features iteratively

### Dependencies
- Sprint 3 completion (change management functional)
- Understanding of CMDB concepts and homelab infrastructure

## Success Metrics

- [ ] CMDB tracks all major homelab infrastructure types
- [ ] CI relationships accurately model dependencies
- [ ] Integration with issues and changes demonstrates value
- [ ] Minimum 25 BDD scenarios passing
- [ ] Tutorial enables building first CMDB
- [ ] Sprint goal achieved: Complete ITIL trilogy (Incident, Change, Configuration)
