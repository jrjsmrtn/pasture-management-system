<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# CMDB Schema Reference

## Overview

The Configuration Management Database (CMDB) schema in the Pasture Management System provides a comprehensive structure for tracking homelab infrastructure Configuration Items (CIs), their attributes, relationships, and lifecycle states.

## Configuration Item (CI) Class

The `ci` class is the core entity in the CMDB, representing any trackable component in your homelab infrastructure.

### Base Attributes

All Configuration Items include these common attributes:

| Field         | Type                | Required | Description                                                          |
| ------------- | ------------------- | -------- | -------------------------------------------------------------------- |
| `name`        | String              | Yes      | Unique name identifying the CI (e.g., "db-server-01", "core-switch") |
| `type`        | Link(citype)        | Yes      | CI type classification (Server, Network Device, Storage, etc.)       |
| `status`      | Link(cistatus)      | Yes      | Current lifecycle status (Planning, Active, Retired, etc.)           |
| `location`    | String              | No       | Physical or logical location (e.g., "Rack 1, Unit 5", "DC East")     |
| `owner`       | Link(user)          | No       | Person responsible for the CI                                        |
| `criticality` | Link(cicriticality) | No       | Business criticality level (Very Low to Very High)                   |
| `description` | String              | No       | Detailed description of the CI                                       |

### Automatic Attributes

Like all Roundup classes, CIs automatically include:

| Field      | Type       | Description                    |
| ---------- | ---------- | ------------------------------ |
| `creation` | Date       | Timestamp when CI was created  |
| `activity` | Date       | Timestamp of last modification |
| `creator`  | Link(user) | User who created the CI        |
| `actor`    | Link(user) | User who last modified the CI  |

### Type-Specific Attributes

Different CI types use different subsets of these optional attributes:

#### Server Attributes

| Field        | Type   | Description                                 |
| ------------ | ------ | ------------------------------------------- |
| `cpu_cores`  | Number | Number of CPU cores                         |
| `ram_gb`     | Number | RAM capacity in gigabytes                   |
| `os`         | String | Operating system (e.g., "Ubuntu 24.04 LTS") |
| `ip_address` | String | Primary IP address                          |

**Example:**

```json
{
  "name": "db-server-01",
  "type": "1",  // Server
  "status": "5",  // Active
  "location": "Rack 1, Unit 5",
  "criticality": "4",  // High
  "cpu_cores": 8,
  "ram_gb": 32,
  "os": "Ubuntu 24.04 LTS",
  "ip_address": "192.168.1.50"
}
```

#### Network Device Attributes

| Field        | Type   | Description                              |
| ------------ | ------ | ---------------------------------------- |
| `ip_address` | String | Management IP address                    |
| `ports`      | Number | Number of network ports                  |
| `vendor`     | String | Manufacturer (e.g., "Cisco", "Ubiquiti") |

**Example:**

```json
{
  "name": "core-switch-01",
  "type": "2",  // Network Device
  "status": "5",  // Active
  "location": "Network closet",
  "criticality": "5",  // Very High
  "ip_address": "192.168.1.1",
  "ports": 48,
  "vendor": "Ubiquiti"
}
```

#### Storage Attributes

| Field         | Type   | Description                   |
| ------------- | ------ | ----------------------------- |
| `capacity_gb` | Number | Storage capacity in gigabytes |
| `vendor`      | String | Manufacturer                  |

**Example:**

```json
{
  "name": "nas-01",
  "type": "3",  // Storage
  "status": "5",  // Active
  "capacity_gb": 8000,
  "vendor": "Synology"
}
```

#### Software/Service Attributes

| Field     | Type   | Description             |
| --------- | ------ | ----------------------- |
| `version` | String | Software version number |
| `vendor`  | String | Vendor or project name  |

**Example:**

```json
{
  "name": "postgres-db",
  "type": "4",  // Software
  "status": "5",  // Active
  "version": "16.1",
  "vendor": "PostgreSQL Global Development Group"
}
```

#### Virtual Machine Attributes

| Field        | Type   | Description            |
| ------------ | ------ | ---------------------- |
| `cpu_cores`  | Number | Allocated vCPUs        |
| `ram_gb`     | Number | Allocated RAM in GB    |
| `os`         | String | Guest operating system |
| `ip_address` | String | Primary IP address     |

**Example:**

```json
{
  "name": "app-vm-01",
  "type": "6",  // Virtual Machine
  "status": "5",  // Active
  "cpu_cores": 4,
  "ram_gb": 16,
  "os": "Debian 12",
  "ip_address": "192.168.1.100"
}
```

### Relationship Attributes

CIs can be linked to issues and changes:

| Field             | Type              | Description               |
| ----------------- | ----------------- | ------------------------- |
| `related_issues`  | Multilink(issue)  | Issues affecting this CI  |
| `related_changes` | Multilink(change) | Changes targeting this CI |

## CI Type Classifications

The `citype` class defines the categories of Configuration Items.

| ID  | Name            | Order | Description                                  |
| --- | --------------- | ----- | -------------------------------------------- |
| 1   | Server          | 1     | Physical or bare-metal servers               |
| 2   | Network Device  | 2     | Switches, routers, firewalls, access points  |
| 3   | Storage         | 3     | NAS, SAN, storage arrays                     |
| 4   | Software        | 4     | Installed software packages and applications |
| 5   | Service         | 5     | Running services and daemons                 |
| 6   | Virtual Machine | 6     | VMs running on hypervisors                   |

## CI Lifecycle Statuses

The `cistatus` class tracks the lifecycle state of Configuration Items.

| ID  | Name        | Order | Description                  | Typical Use                     |
| --- | ----------- | ----- | ---------------------------- | ------------------------------- |
| 1   | Planning    | 1     | CI is being planned          | Hardware being researched       |
| 2   | Ordered     | 2     | CI has been ordered          | Waiting for delivery            |
| 3   | In Stock    | 3     | CI received but not deployed | Sitting in inventory            |
| 4   | Deployed    | 4     | CI deployed but not active   | Installed but not in production |
| 5   | Active      | 5     | CI is in production use      | Normal operational state        |
| 6   | Maintenance | 6     | CI undergoing maintenance    | Temporarily offline for updates |
| 7   | Retired     | 7     | CI decommissioned            | No longer in use                |

### Lifecycle Flow

Typical CI lifecycle progression:

```
Planning → Ordered → In Stock → Deployed → Active
                                              ↓
                                         Maintenance ⇄ Active
                                              ↓
                                           Retired
```

## CI Criticality Levels

The `cicriticality` class indicates the business impact if a CI fails.

| ID  | Name      | Order | Description                 | Impact Example                    |
| --- | --------- | ----- | --------------------------- | --------------------------------- |
| 1   | Very Low  | 1     | Minimal business impact     | Test server failure               |
| 2   | Low       | 2     | Limited business impact     | Development workstation down      |
| 3   | Medium    | 3     | Moderate business impact    | Non-critical service interruption |
| 4   | High      | 4     | Significant business impact | Database server failure           |
| 5   | Very High | 5     | Critical business impact    | Core network switch failure       |

### Criticality Assessment Criteria

When assigning criticality, consider:

- **Availability requirement**: How much uptime is needed?
- **User impact**: How many users/services depend on this CI?
- **Recovery time**: How quickly must it be restored?
- **Data sensitivity**: Does it handle critical data?
- **Business continuity**: Is it a single point of failure?

## CI Relationships

The `cirelationship` class models dependencies between Configuration Items.

### Relationship Schema

| Field               | Type                     | Required | Description                        |
| ------------------- | ------------------------ | -------- | ---------------------------------- |
| `source_ci`         | Link(ci)                 | Yes      | The CI initiating the relationship |
| `relationship_type` | Link(cirelationshiptype) | Yes      | Type of relationship               |
| `target_ci`         | Link(ci)                 | Yes      | The CI being related to            |
| `description`       | String                   | No       | Additional context                 |

### Relationship Types

| ID  | Name         | Order | Description                                    | Example                          |
| --- | ------------ | ----- | ---------------------------------------------- | -------------------------------- |
| 1   | Runs On      | 1     | VM/software runs on server                     | app-vm-01 Runs On db-server-01   |
| 2   | Hosts        | 2     | Server hosts VM (inverse of Runs On)           | db-server-01 Hosts app-vm-01     |
| 3   | Depends On   | 3     | Service depends on another CI                  | web-service Depends On database  |
| 4   | Required By  | 4     | CI required by another (inverse of Depends On) | database Required By web-service |
| 5   | Connects To  | 5     | Network connection                             | server Connects To switch        |
| 6   | Contains     | 6     | Physical containment                           | rack Contains server             |
| 7   | Contained By | 7     | Inverse of Contains                            | server Contained By rack         |

### Bidirectional Relationships

Most relationships are bidirectional. When you create:

```
VM-1 "Runs On" Server-1
```

The system should automatically create:

```
Server-1 "Hosts" VM-1
```

### Relationship Examples

#### Virtual Infrastructure

```
app-vm-01 (VM)
  └─ Runs On: hypervisor-01 (Server)
     └─ Hosts: app-vm-01, db-vm-01, web-vm-01
```

#### Service Dependencies

```
web-app (Service)
  ├─ Depends On: app-server (VM)
  ├─ Depends On: database (Service)
  └─ Depends On: cache (Service)
```

#### Network Topology

```
server-01 (Server)
  ├─ Connects To: switch-01 (Network Device)
  └─ Connects To: mgmt-switch (Network Device)
```

## API Endpoints

### Schema Endpoint

```
GET /api/schema/ci
```

Returns the complete CI schema including field definitions and types.

### Type-Specific Schema

```
GET /api/schema/ci/server
GET /api/schema/ci/network_device
GET /api/schema/ci/storage
GET /api/schema/ci/software
GET /api/schema/ci/service
GET /api/schema/ci/virtual_machine
```

Returns type-specific attribute definitions.

## CLI Usage

### Query CI Schema

```bash
roundup-admin -i tracker table ci
```

### List CI Types

```bash
roundup-admin -i tracker list citype
```

### List CI Statuses

```bash
roundup-admin -i tracker list cistatus
```

## Validation Rules

### Required Fields

- `name`: Must be non-empty string
- `type`: Must be valid CI type ID
- `status`: Must be valid CI status ID

### Constraints

- `name`: Should be unique within a type for clarity
- `cpu_cores`, `ram_gb`, `ports`, `capacity_gb`: Must be positive numbers if provided
- `criticality`: Recommended for production CIs
- `owner`: Recommended for accountability

### Circular Dependency Prevention

The system should detect and prevent circular relationships:

```
❌ INVALID:
CI-A Depends On CI-B
CI-B Depends On CI-C
CI-C Depends On CI-A  // Circular!
```

## See Also

- [CI Relationship Types](./ci-relationships.md) - Detailed relationship modeling
- [Creating Configuration Items](../howto/create-configuration-item.md) - How-to guide
- [Understanding CMDB](../explanation/cmdb-concepts.md) - Conceptual overview
- [Building Your Homelab CMDB](../tutorials/building-homelab-cmdb.md) - Tutorial

## Revision History

| Date       | Version | Changes                           |
| ---------- | ------- | --------------------------------- |
| 2025-11-16 | 0.5.0   | Initial CMDB schema documentation |
