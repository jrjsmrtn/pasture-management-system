<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# CI Relationship Types Reference

## Overview

This reference document defines all Configuration Item (CI) relationship types available in the Pasture Management System. Relationships model dependencies, hosting, connectivity, and containment between infrastructure components.

**Last Updated**: 2025-11-20
**Version**: 1.0.0

## Relationship Schema

### Database Schema

```python
cirelationship = Class(db, "cirelationship",
    source_ci       = Link("ci", do_journal='no'),
    relationship_type = Link("cirelationshiptype", do_journal='no'),
    target_ci       = Link("ci", do_journal='no'),
    description     = String(do_journal='yes'),
)
```

### Fields

| Field               | Type                     | Required | Description                                         |
| ------------------- | ------------------------ | -------- | --------------------------------------------------- |
| `source_ci`         | Link(ci)                 | Yes      | The CI initiating the relationship                  |
| `relationship_type` | Link(cirelationshiptype) | Yes      | Type of relationship (1-7)                          |
| `target_ci`         | Link(ci)                 | Yes      | The CI being related to                             |
| `description`       | String                   | No       | Additional context about this specific relationship |

## Relationship Types

### Type 1: Runs On

**Direction**: Software/Virtual → Hardware/Platform

**Definition**: The source CI executes on or is hosted by the target CI.

**Use Cases**:

- Virtual Machine → Physical Server
- Container → Docker Host
- Service/Daemon → Server
- Application → Operating System
- VM → Hypervisor

**Examples**:

```
db-vm-01 (Virtual Machine) "Runs On" hypervisor-01 (Server)
postgresql-service (Service) "Runs On" db-vm-01 (Virtual Machine)
nginx-container (Service) "Runs On" docker-host (Server)
web-app (Software) "Runs On" app-server-vm (Virtual Machine)
```

**Impact Analysis**:

- If target fails → source fails
- If target undergoes maintenance → source is unavailable
- If target is rebooted → source is restarted

**CLI Example**:

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=7 \
  relationship_type=1 \
  target_ci=5 \
  description="Database VM hosted on primary hypervisor"
```

**Inverse Relationship**: "Hosts" (Type 2)

______________________________________________________________________

### Type 2: Hosts

**Direction**: Hardware/Platform → Software/Virtual

**Definition**: The source CI provides hosting/execution environment for the target CI.

**Use Cases**:

- Physical Server → Virtual Machine
- Docker Host → Container
- Hypervisor → VMs
- Operating System → Services

**Examples**:

```
hypervisor-01 (Server) "Hosts" db-vm-01 (Virtual Machine)
docker-host (Server) "Hosts" nginx-container (Service)
app-server-vm (Virtual Machine) "Hosts" web-app (Software)
```

**Impact Analysis**:

- If source fails → all hosted targets fail
- Source capacity determines how many targets can be hosted
- Useful for capacity planning queries

**CLI Example**:

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=5 \
  relationship_type=2 \
  target_ci=7 \
  description="Hypervisor hosts database VM with 4 vCPUs, 16GB RAM"
```

**Inverse Relationship**: "Runs On" (Type 1)

**Query Pattern**:

```bash
# Find all VMs on a hypervisor
cd tracker
uv run roundup-admin -i . find cirelationship source_ci=5 relationship_type=2
```

______________________________________________________________________

### Type 3: Depends On

**Direction**: Service/Application → Service/Resource

**Definition**: The source CI requires the target CI to function properly.

**Use Cases**:

- Application → Database
- Service → Authentication Service
- Web App → Cache Server
- Frontend → Backend API
- Microservice → Microservice

**Examples**:

```
web-app (Service) "Depends On" postgresql-db (Service)
api-gateway (Service) "Depends On" auth-service (Service)
wordpress (Software) "Depends On" mysql-db (Service)
grafana (Service) "Depends On" prometheus (Service)
```

**Impact Analysis**:

- If target is unavailable → source fails or degrades
- Critical for understanding cascading failures
- Essential for change impact analysis

**CLI Example**:

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=11 \
  relationship_type=3 \
  target_ci=10 \
  description="Web app requires PostgreSQL for user authentication and data storage"
```

**Inverse Relationship**: "Required By" (Type 4)

**Query Pattern**:

```bash
# Find all services that depend on a database
cd tracker
uv run roundup-admin -i . find cirelationship target_ci=10 relationship_type=3
```

**Criticality Assessment**:

When creating dependencies, consider:

- **Hard Dependency**: Source completely fails if target unavailable
- **Soft Dependency**: Source degrades but continues with reduced functionality
- **Optional Dependency**: Source works but loses a feature

Document in the relationship description field.

______________________________________________________________________

### Type 4: Required By

**Direction**: Service/Resource → Service/Application

**Definition**: The source CI is required by the target CI.

**Use Cases**:

- Database → Applications using it
- Authentication Service → Dependent services
- Shared Library → Applications
- Central Logging → Services that log to it

**Examples**:

```
postgresql-db (Service) "Required By" web-app (Service)
auth-service (Service) "Required By" api-gateway (Service)
redis-cache (Service) "Required By" session-manager (Service)
```

**Impact Analysis**:

- Identifies critical CIs (many dependents = critical)
- Useful for prioritizing maintenance and monitoring
- Shows blast radius of potential failures

**CLI Example**:

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=10 \
  relationship_type=4 \
  target_ci=11 \
  description="PostgreSQL required by web application"
```

**Inverse Relationship**: "Depends On" (Type 3)

**Query Pattern**:

```bash
# Find all services that require a specific component
cd tracker
uv run roundup-admin -i . find cirelationship source_ci=10 relationship_type=4
```

**Best Practice**: Usually sufficient to document one direction ("Depends On" or "Required By"), not both.

______________________________________________________________________

### Type 5: Connects To

**Direction**: Bidirectional (network connectivity)

**Definition**: The source CI has network connectivity to the target CI.

**Use Cases**:

- Server → Switch
- Switch → Router
- Switch → Switch (uplink)
- Client → Server
- Network Device → Network Device

**Examples**:

```
server-01 (Server) "Connects To" core-switch (Network Device)
core-switch (Network Device) "Connects To" router-01 (Network Device)
access-switch (Network Device) "Connects To" core-switch (Network Device)
workstation (Server) "Connects To" vpn-server (Service)
```

**Impact Analysis**:

- Maps network topology
- Identifies single points of failure
- Troubleshooting connectivity issues

**CLI Example**:

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=5 \
  relationship_type=5 \
  target_ci=2 \
  description="Server connected to core switch port 12 (1Gbps)"
```

**Extended Description**:

Include in description:

- Port number
- Link speed
- VLAN information
- Physical cable identifier

**Query Pattern**:

```bash
# Find all devices connected to a switch
cd tracker
uv run roundup-admin -i . find cirelationship target_ci=2 relationship_type=5
```

**Network Diagram Generation**:

Query all "Connects To" relationships to generate network topology diagrams.

______________________________________________________________________

### Type 6: Contains

**Direction**: Container → Contained

**Definition**: The source CI physically or logically contains the target CI.

**Use Cases**:

- Rack → Servers in rack
- Chassis → Blade Servers
- Building → Rooms
- Room → Racks
- Data Center → Rows

**Examples**:

```
server-rack-01 (Storage) "Contains" server-01 (Server)
server-rack-01 (Storage) "Contains" server-02 (Server)
blade-chassis (Server) "Contains" blade-01 (Server)
network-closet (Location) "Contains" core-switch (Network Device)
```

**Impact Analysis**:

- Physical location tracking
- Capacity planning for racks/rooms
- Physical access requirements

**CLI Example**:

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=25 \
  relationship_type=6 \
  target_ci=5 \
  description="Server rack unit 5-7, 4U chassis"
```

**Extended Description**:

Include in description:

- Rack unit (U) position
- Physical dimensions
- Power consumption
- Cooling requirements

**Inverse Relationship**: "Contained By" (Type 7)

______________________________________________________________________

### Type 7: Contained By

**Direction**: Contained → Container

**Definition**: The source CI is physically or logically contained by the target CI.

**Use Cases**:

- Server → Rack
- Blade Server → Chassis
- Equipment → Room
- Disk Drive → Storage Array

**Examples**:

```
server-01 (Server) "Contained By" server-rack-01 (Storage)
core-switch (Network Device) "Contained By" network-closet (Location)
disk-01 (Storage) "Contained By" nas-01 (Storage)
```

**Impact Analysis**:

- Physical inventory management
- Disaster recovery planning
- Physical security zones

**CLI Example**:

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=5 \
  relationship_type=7 \
  target_ci=25 \
  description="Server mounted in rack unit 5-7"
```

**Inverse Relationship**: "Contains" (Type 6)

**Best Practice**: Usually sufficient to document one direction ("Contains" or "Contained By"), not both.

______________________________________________________________________

## Relationship Type Summary Table

| Type | Name         | Direction | Inverse | Common Use Cases                      |
| ---- | ------------ | --------- | ------- | ------------------------------------- |
| 1    | Runs On      | SW → HW   | 2       | VM→Server, Service→VM, Container→Host |
| 2    | Hosts        | HW → SW   | 1       | Server→VM, Hypervisor→VMs             |
| 3    | Depends On   | SVC → SVC | 4       | App→DB, Frontend→Backend              |
| 4    | Required By  | SVC → SVC | 3       | DB→App, API→Clients                   |
| 5    | Connects To  | NET ↔ NET | 5       | Server→Switch, Switch→Router          |
| 6    | Contains     | PHY → PHY | 7       | Rack→Server, Chassis→Blade            |
| 7    | Contained By | PHY → PHY | 6       | Server→Rack, Blade→Chassis            |

**Legend**:

- SW = Software/Virtual
- HW = Hardware/Physical
- SVC = Service/Application
- NET = Network connectivity
- PHY = Physical containment

## Choosing the Right Relationship Type

### Decision Tree

```
Question 1: Is this about physical location?
├─ Yes → Use "Contains" (6) or "Contained By" (7)
└─ No → Question 2

Question 2: Is this about network connectivity?
├─ Yes → Use "Connects To" (5)
└─ No → Question 3

Question 3: Is this about hosting/execution?
├─ Yes → Use "Runs On" (1) or "Hosts" (2)
└─ No → Question 4

Question 4: Is this about service dependencies?
└─ Yes → Use "Depends On" (3) or "Required By" (4)
```

### Examples

**Scenario**: PostgreSQL database service running on a VM

```
postgresql-service (Service) "Runs On" db-vm-01 (Virtual Machine)
```

Reasoning: Service executes on the VM → Type 1 (Runs On)

**Scenario**: Web application needs database to function

```
web-app (Service) "Depends On" postgresql-service (Service)
```

Reasoning: Web app requires database → Type 3 (Depends On)

**Scenario**: Server plugged into network switch

```
server-01 (Server) "Connects To" core-switch (Network Device)
```

Reasoning: Network connection → Type 5 (Connects To)

**Scenario**: Server mounted in rack

```
server-rack-01 (Storage) "Contains" server-01 (Server)
```

Reasoning: Physical containment → Type 6 (Contains)

## API Reference

### REST API Endpoints

#### Create Relationship

```http
POST /rest/data/cirelationship
Content-Type: application/json

{
  "source_ci": "7",
  "relationship_type": "1",
  "target_ci": "5",
  "description": "Database VM hosted on hypervisor"
}
```

#### Query Relationships

```http
GET /rest/data/cirelationship?source_ci=7
GET /rest/data/cirelationship?target_ci=5
GET /rest/data/cirelationship?relationship_type=1
```

#### Update Relationship

```http
PATCH /rest/data/cirelationship/1
Content-Type: application/json

{
  "description": "Updated description"
}
```

#### Delete Relationship

```http
DELETE /rest/data/cirelationship/1
```

### CLI Commands

#### Create

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=SOURCE_ID \
  relationship_type=TYPE_ID \
  target_ci=TARGET_ID \
  description="Optional description"
```

#### List

```bash
cd tracker
uv run roundup-admin -i . list cirelationship
```

#### Find

```bash
cd tracker
# By source
uv run roundup-admin -i . find cirelationship source_ci=7

# By target
uv run roundup-admin -i . find cirelationship target_ci=5

# By type
uv run roundup-admin -i . find cirelationship relationship_type=1

# Combined filters
uv run roundup-admin -i . find cirelationship source_ci=7 relationship_type=1
```

#### Get Details

```bash
cd tracker
uv run roundup-admin -i . get cirelationship1
```

#### Update

```bash
cd tracker
uv run roundup-admin -i . set cirelationship1 description="Updated description"
```

#### Delete

```bash
cd tracker
uv run roundup-admin -i . retire cirelationship1
```

## Validation Rules

### Required Fields

All relationships must have:

- `source_ci`: Valid CI ID (must exist in database)
- `relationship_type`: Valid type ID (1-7)
- `target_ci`: Valid CI ID (must exist in database)

### Constraints

- **Self-Reference**: Source and target must be different CIs
- **Uniqueness**: Same source→target→type combination should not be duplicated
- **Circular Dependencies**: Should be avoided for "Depends On" relationships

### Recommended Practices

- **Description**: Include for complex or critical relationships
- **Documentation**: Explain why the relationship exists
- **Context**: Add technical details (port numbers, versions, etc.)

## Common Patterns

### Pattern 1: Full Stack Dependency

```
web-frontend (Service)
  └── Depends On: api-backend (Service)
        └── Depends On: postgresql-db (Service)
              └── Runs On: db-vm (Virtual Machine)
                    └── Runs On: hypervisor (Server)
                          └── Connects To: core-switch (Network Device)
                                └── Connects To: router (Network Device)
```

### Pattern 2: Virtualization Infrastructure

```
hypervisor-01 (Server)
  ├── Hosts: vm-01 (Virtual Machine)
  ├── Hosts: vm-02 (Virtual Machine)
  ├── Hosts: vm-03 (Virtual Machine)
  └── Connects To: core-switch (Network Device)

vm-01 (Virtual Machine)
  └── Hosts: postgresql-service (Service)
```

### Pattern 3: Network Topology

```
router (Network Device)
  └── Connects To: core-switch (Network Device)
        ├── Connects To: access-switch-01 (Network Device)
        ├── Connects To: access-switch-02 (Network Device)
        ├── Connects To: server-01 (Server)
        └── Connects To: server-02 (Server)
```

## Troubleshooting

### Relationship Not Created

**Problem**: CLI command succeeds but relationship not visible

**Diagnosis**:

```bash
cd tracker
# Verify source CI exists
uv run roundup-admin -i . get ci7

# Verify target CI exists
uv run roundup-admin -i . get ci5

# Verify relationship type is valid (1-7)
```

**Solution**: Ensure all referenced CIs exist before creating relationship.

### Duplicate Relationships

**Problem**: Same relationship documented multiple times

**Diagnosis**:

```bash
cd tracker
uv run roundup-admin -i . find cirelationship source_ci=7 target_ci=5 relationship_type=1
```

**Solution**: Remove duplicates:

```bash
cd tracker
uv run roundup-admin -i . retire cirelationship2
```

### Circular Dependencies Detected

**Problem**: CI-A depends on CI-B which depends on CI-A

**Diagnosis**:

```bash
cd tracker
# Trace dependency chain
uv run roundup-admin -i . find cirelationship source_ci=A
uv run roundup-admin -i . find cirelationship source_ci=B
```

**Solution**: Review architecture and break circular dependency at application level.

## See Also

- **How-to**: [Documenting Infrastructure Dependencies](../howto/documenting-infrastructure-dependencies.md)
- **Reference**: [CMDB Schema](./cmdb-schema.md)
- **Tutorial**: [Building Your Homelab CMDB](../tutorials/building-homelab-cmdb.md)
- **Explanation**: [Why Configuration Management Matters](../explanation/why-configuration-management.md)

## Revision History

| Date       | Version | Changes                                 |
| ---------- | ------- | --------------------------------------- |
| 2025-11-20 | 1.0.0   | Initial CI relationship types reference |
