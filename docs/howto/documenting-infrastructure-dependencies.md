<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How to Document Infrastructure Dependencies

## Overview

This guide shows you how to document relationships and dependencies between Configuration Items (CIs) in your homelab infrastructure. Proper dependency documentation enables impact analysis, troubleshooting, and change planning.

**Time Required**: 10-15 minutes per CI
**Difficulty**: Beginner
**Prerequisites**: CIs created in CMDB

## Why Document Dependencies?

### Impact Analysis

**Before making changes**, know what will be affected:

```
Scenario: Need to reboot hypervisor for updates

Query: What depends on this hypervisor?
Result: 3 VMs → 5 services → 2 web apps

Decision: Schedule maintenance window, notify users
```

### Faster Troubleshooting

**When things break**, understand the dependency chain:

```
Symptom: Web app down
Dependency Chain: web-app → database-vm → hypervisor → storage-nas
Investigation: Check each component in order
Root Cause: Storage NAS disk failure
```

### Knowledge Retention

**Months later**, remember how things connect:

- Which services run on which servers?
- What networking equipment connects where?
- Which databases support which applications?

## Relationship Types

PMS supports these relationship types:

| Type         | ID  | Description                  | Example                      |
| ------------ | --- | ---------------------------- | ---------------------------- |
| Runs On      | 1   | VM/software runs on hardware | app-vm Runs On server-01     |
| Hosts        | 2   | Server hosts VM/service      | server-01 Hosts app-vm       |
| Depends On   | 3   | Service depends on another   | web-app Depends On database  |
| Required By  | 4   | Service required by another  | database Required By web-app |
| Connects To  | 5   | Network connection           | server Connects To switch    |
| Contains     | 6   | Physical containment         | rack Contains server         |
| Contained By | 7   | Inverse of Contains          | server Contained By rack     |

See [CI Relationship Types](../reference/ci-relationship-types.md) for detailed definitions.

## Common Dependency Patterns

### Pattern 1: Virtual Machine Hosting

**Scenario**: VMs running on physical hypervisor

```
Hypervisor (Physical Server)
  ├── VM 1 "Runs On" Hypervisor
  ├── VM 2 "Runs On" Hypervisor
  └── VM 3 "Runs On" Hypervisor
```

**CLI Commands**:

```bash
cd tracker
# Find hypervisor CI ID
uv run roundup-admin -i . find ci name=hypervisor-01

# Create relationships (assuming hypervisor is ci5, VMs are ci7, ci8, ci9)
uv run roundup-admin -i . create cirelationship \
  source_ci=7 \
  relationship_type=1 \
  target_ci=5

uv run roundup-admin -i . create cirelationship \
  source_ci=8 \
  relationship_type=1 \
  target_ci=5

uv run roundup-admin -i . create cirelationship \
  source_ci=9 \
  relationship_type=1 \
  target_ci=5
```

**Impact**: If hypervisor fails → all 3 VMs fail

### Pattern 2: Service Dependencies

**Scenario**: Web application depends on database

```
Web Application (Service)
  ├── "Runs On" web-server-vm
  └── "Depends On" database-service
```

**CLI Commands**:

```bash
cd tracker
# Create "Runs On" relationship
uv run roundup-admin -i . create cirelationship \
  source_ci=11 \
  relationship_type=1 \
  target_ci=8

# Create "Depends On" relationship
uv run roundup-admin -i . create cirelationship \
  source_ci=11 \
  relationship_type=3 \
  target_ci=10
```

**Impact**: If database fails → web application fails

### Pattern 3: Multi-Tier Application

**Scenario**: 3-tier web application stack

```
Load Balancer
  └── Connects To: Web Server 1, Web Server 2

Web Server 1 & 2
  └── Depends On: Application Server

Application Server
  ├── Depends On: Database Server
  └── Depends On: Cache Server
```

**CLI Commands**:

```bash
cd tracker
# Load balancer connections
uv run roundup-admin -i . create cirelationship \
  source_ci=15 \
  relationship_type=5 \
  target_ci=16

uv run roundup-admin -i . create cirelationship \
  source_ci=15 \
  relationship_type=5 \
  target_ci=17

# Web server dependencies
uv run roundup-admin -i . create cirelationship \
  source_ci=16 \
  relationship_type=3 \
  target_ci=18

uv run roundup-admin -i . create cirelationship \
  source_ci=17 \
  relationship_type=3 \
  target_ci=18

# Application server dependencies
uv run roundup-admin -i . create cirelationship \
  source_ci=18 \
  relationship_type=3 \
  target_ci=19

uv run roundup-admin -i . create cirelationship \
  source_ci=18 \
  relationship_type=3 \
  target_ci=20
```

### Pattern 4: Network Topology

**Scenario**: Servers connected to switches

```
Core Switch
  ├── Connects To: Router
  ├── Connects To: Server 1
  ├── Connects To: Server 2
  └── Connects To: Access Switch

Access Switch
  ├── Connects To: Core Switch
  └── Connects To: Access Point
```

**CLI Commands**:

```bash
cd tracker
# Core switch to router
uv run roundup-admin -i . create cirelationship \
  source_ci=2 \
  relationship_type=5 \
  target_ci=1

# Core switch to servers
uv run roundup-admin -i . create cirelationship \
  source_ci=5 \
  relationship_type=5 \
  target_ci=2

uv run roundup-admin -i . create cirelationship \
  source_ci=6 \
  relationship_type=5 \
  target_ci=2

# Core switch to access switch
uv run roundup-admin -i . create cirelationship \
  source_ci=3 \
  relationship_type=5 \
  target_ci=2
```

**Impact**: If core switch fails → all connected devices lose connectivity

### Pattern 5: Container Hosting

**Scenario**: Containers running on Docker host

```
Docker Host (Physical Server)
  ├── Container 1 "Runs On" Docker Host
  ├── Container 2 "Runs On" Docker Host
  └── Container 3 "Runs On" Docker Host

Container 1 (PostgreSQL)
  └── Required By: Container 2 (Web App)
```

**CLI Commands**:

```bash
cd tracker
# Create container CIs (type=5 for services)
uv run roundup-admin -i . create ci \
  name="postgres-container" \
  type=5 \
  status=5

uv run roundup-admin -i . create ci \
  name="webapp-container" \
  type=5 \
  status=5

# Containers run on Docker host
uv run roundup-admin -i . create cirelationship \
  source_ci=21 \
  relationship_type=1 \
  target_ci=6

uv run roundup-admin -i . create cirelationship \
  source_ci=22 \
  relationship_type=1 \
  target_ci=6

# Web app depends on database
uv run roundup-admin -i . create cirelationship \
  source_ci=22 \
  relationship_type=3 \
  target_ci=21
```

### Pattern 6: Storage Dependencies

**Scenario**: VMs using shared storage

```
NAS Storage
  └── Hosts: VM Datastore

VM Datastore
  ├── Hosts: VM 1 (disk image)
  ├── Hosts: VM 2 (disk image)
  └── Hosts: VM 3 (disk image)
```

**CLI Commands**:

```bash
cd tracker
# Create datastore CI
uv run roundup-admin -i . create ci \
  name="vm-datastore-01" \
  type=3 \
  status=5 \
  location="nas-ds920plus"

# Datastore hosted on NAS
uv run roundup-admin -i . create cirelationship \
  source_ci=23 \
  relationship_type=1 \
  target_ci=4

# VMs depend on datastore
uv run roundup-admin -i . create cirelationship \
  source_ci=7 \
  relationship_type=3 \
  target_ci=23

uv run roundup-admin -i . create cirelationship \
  source_ci=8 \
  relationship_type=3 \
  target_ci=23
```

**Impact**: If NAS fails → all VMs on that datastore fail

## Discovering Dependencies

### Method 1: Network Mapping

**Tool**: nmap, traceroute

```bash
# Scan network to discover connectivity
nmap -sn 192.168.1.0/24

# For each host, trace route to identify switches/routers
traceroute 192.168.1.50
```

Document discovered connections as "Connects To" relationships.

### Method 2: Service Configuration

**Tool**: Configuration files

```bash
# Check web app config for database connection
cat /etc/webapp/config.yml

# Example output:
database:
  host: db-server-vm
  port: 5432
```

Document as "Depends On" relationship: webapp → database

### Method 3: Process Inspection

**Tool**: ps, netstat, lsof

```bash
# Find processes and their network connections
netstat -tupn

# Example output:
tcp  0  0  192.168.1.51:80  192.168.1.50:5432  ESTABLISHED  1234/nginx

# Interpretation: Web server (192.168.1.51) connected to database (192.168.1.50)
```

Document as service dependency.

### Method 4: Infrastructure as Code

**Tool**: Ansible, Terraform, Docker Compose

```yaml
# docker-compose.yml
services:
  web:
    depends_on:
      - db
      - cache
  db:
    image: postgres:16
  cache:
    image: redis:7
```

Document these dependencies in CMDB.

## Verifying Relationships

### Query Relationships

**Find all relationships for a CI**:

```bash
cd tracker
# Find relationships where CI is source
uv run roundup-admin -i . find cirelationship source_ci=11

# Find relationships where CI is target
uv run roundup-admin -i . find cirelationship target_ci=11
```

### Visualize Dependency Chain

**Use Web UI**:

1. Navigate to http://localhost:9080/pms/ci11
1. Scroll to "Relationships" section
1. Review outgoing and incoming relationships

### Test Impact Analysis

**Scenario**: What happens if I reboot this server?

```bash
cd tracker
# Find all CIs running on this server
uv run roundup-admin -i . find cirelationship target_ci=5 relationship_type=1

# For each dependent CI, find its dependents
uv run roundup-admin -i . find cirelationship source_ci=7 relationship_type=3
```

**Result**: Complete dependency chain showing impact

## Maintenance Tasks

### Regular Audits

**Monthly**: Verify relationships are current

```bash
cd tracker
# List all relationships
uv run roundup-admin -i . list cirelationship

# Review each relationship:
# - Does it still exist in reality?
# - Is the relationship type correct?
# - Are there new relationships to document?
```

### Update After Changes

**When you deploy new infrastructure**:

1. Create CI for new component
1. Document relationships
1. Update dependent CIs if needed

**Example**:

```bash
cd tracker
# Deployed new cache server
uv run roundup-admin -i . create ci \
  name="redis-cache" \
  type=5 \
  status=5

# Web app now depends on cache
uv run roundup-admin -i . create cirelationship \
  source_ci=11 \
  relationship_type=3 \
  target_ci=24
```

### Remove Obsolete Relationships

**When decommissioning infrastructure**:

```bash
cd tracker
# Find relationships involving retired CI
uv run roundup-admin -i . find cirelationship source_ci=8

# Delete each relationship
uv run roundup-admin -i . retire cirelationship1
```

## Best Practices

### 1. Document Critical Dependencies First

**Priority Order**:

1. Production services and their direct dependencies
1. Infrastructure hosting production services
1. Network connectivity for production
1. Development/test environments (lower priority)

### 2. Use Consistent Relationship Types

**Hosting**:

- VM → Server: "Runs On"
- Container → Host: "Runs On"
- Service → VM: "Runs On"

**Service Dependencies**:

- App → Database: "Depends On"
- App → Cache: "Depends On"
- Frontend → Backend: "Depends On"

**Network**:

- Server → Switch: "Connects To"
- Switch → Router: "Connects To"

### 3. Bidirectional Relationships

Some relationships have inverses:

- "Runs On" ↔ "Hosts"
- "Depends On" ↔ "Required By"
- "Contains" ↔ "Contained By"

**You can document both**, but one direction is usually sufficient for impact analysis.

### 4. Add Descriptions for Complex Relationships

```bash
cd tracker
uv run roundup-admin -i . create cirelationship \
  source_ci=11 \
  relationship_type=3 \
  target_ci=10 \
  description="Web app uses database for user authentication and session storage. Critical dependency."
```

### 5. Avoid Circular Dependencies

**Invalid**:

```
❌ CI-A Depends On CI-B
   CI-B Depends On CI-C
   CI-C Depends On CI-A  # Circular!
```

**Solution**: Review architecture to break circular dependencies.

## Use Cases

### Use Case 1: Change Impact Analysis

**Scenario**: Planning to upgrade PostgreSQL database

```bash
cd tracker
# Find the database CI
uv run roundup-admin -i . find ci name=postgresql-service

# Find everything that depends on it
uv run roundup-admin -i . find cirelationship target_ci=10 relationship_type=3

# Result: 3 services depend on this database
# Decision: Schedule maintenance window, test upgrades in dev first
```

### Use Case 2: Troubleshooting Service Outage

**Scenario**: Web app is down

```bash
cd tracker
# Find web app CI
uv run roundup-admin -i . find ci name=web-app-service

# Find its dependencies
uv run roundup-admin -i . find cirelationship source_ci=11

# Result: Depends on db-server-vm and database-service
# Check: Is db-server-vm running? Is database-service responding?
```

### Use Case 3: Capacity Planning

**Scenario**: Adding new VM to hypervisor

```bash
cd tracker
# Find hypervisor
uv run roundup-admin -i . find ci name=hypervisor-01

# Find current VMs on this hypervisor
uv run roundup-admin -i . find cirelationship target_ci=5 relationship_type=1

# Result: 3 VMs currently running
# Check VM resource allocations to ensure capacity
```

### Use Case 4: Security Audit

**Scenario**: Identify all services with database access

```bash
cd tracker
# Find database CI
uv run roundup-admin -i . find ci type=5 name=postgres

# Find all CIs that depend on this database
uv run roundup-admin -i . find cirelationship target_ci=10 relationship_type=3

# Result: List of services with database access
# Review: Are these all authorized? Update firewall rules accordingly
```

## Troubleshooting

### Relationship Not Created

**Problem**: CLI command succeeds but relationship doesn't appear

**Solution**: Verify CI IDs exist:

```bash
cd tracker
uv run roundup-admin -i . get ci11
uv run roundup-admin -i . get ci10
```

If either fails, the CI doesn't exist. Create it first.

### Duplicate Relationships

**Problem**: Same relationship documented twice

**Solution**: Find and remove duplicates:

```bash
cd tracker
# Find all relationships for a CI
uv run roundup-admin -i . find cirelationship source_ci=11 target_ci=10

# If duplicates exist, retire one
uv run roundup-admin -i . retire cirelationship2
```

### Can't Find Relationship in Web UI

**Problem**: Created relationship via CLI but not visible in Web UI

**Solution**: Reindex and restart server:

```bash
cd tracker
uv run roundup-admin -i . reindex cirelationship

pkill -f roundup-server && sleep 2
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```

## Summary

You now know how to:

✅ Understand the 7 relationship types
✅ Document common dependency patterns
✅ Discover dependencies using multiple methods
✅ Verify relationships for accuracy
✅ Maintain relationships over time
✅ Use relationships for impact analysis
✅ Apply best practices for consistency

## Next Steps

- **Reference**: [CI Relationship Types](../reference/ci-relationship-types.md) - Detailed definitions
- **Tutorial**: [Building Your Homelab CMDB](../tutorials/building-homelab-cmdb.md) - Complete example
- **Reference**: [CMDB Schema](../reference/cmdb-schema.md) - Technical details
- **Explanation**: [Why Configuration Management Matters](../explanation/why-configuration-management.md) - Concepts
