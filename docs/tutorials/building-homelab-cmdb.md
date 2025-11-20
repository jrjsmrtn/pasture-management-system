<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Building Your Homelab CMDB

## Introduction

This tutorial walks you through building a complete Configuration Management Database (CMDB) for a realistic homelab environment. You'll learn how to:

- Create Configuration Items (CIs) for your infrastructure
- Document relationships between components
- Use the CMDB for troubleshooting and change management
- Maintain your CMDB over time

By the end of this tutorial, you'll have a working CMDB tracking your entire homelab infrastructure.

## Prerequisites

Before starting, ensure you have:

- Pasture Management System installed (see [Getting Started](./getting-started.md))
- Roundup server running on port 9080
- Admin access to the tracker
- Basic understanding of your homelab infrastructure

## The Example Homelab

We'll build a CMDB for this homelab setup:

### Physical Infrastructure

```
Network Closet:
├── Router: EdgeRouter X (192.168.1.1)
├── Core Switch: UniFi US-24 (192.168.1.2)
└── PoE Switch: UniFi US-8-60W (192.168.1.3)

Server Rack:
├── NAS: Synology DS920+ (192.168.1.10)
├── Server 1: Dell R720 - Hypervisor (192.168.1.20)
└── Server 2: HP ML350 - Docker Host (192.168.1.30)
```

### Virtual Infrastructure

```
Hypervisor (Server 1):
├── VM: Ubuntu DB Server (192.168.1.50)
├── VM: Ubuntu Web Server (192.168.1.51)
└── VM: Debian Monitoring (192.168.1.52)

Docker Host (Server 2):
├── Container: PostgreSQL
├── Container: Redis
└── Container: Nginx Proxy
```

### Services

```
Running Services:
├── PostgreSQL Database (on db-server VM)
├── Web Application (on web-server VM)
├── Prometheus (on monitoring VM)
├── Grafana (on monitoring VM)
└── Nginx Reverse Proxy (container)
```

## Step 1: Set Up Your Database

First, ensure you have a clean database for this tutorial:

```bash
# Reset the database (admin password: admin)
./scripts/reset-test-db.sh admin

# Verify the server is running
curl -s http://localhost:9080/pms/ | grep -q "Roundup" && echo "Server is running"
```

Navigate to http://localhost:9080/pms/ and log in with:

- Username: `admin`
- Password: `admin`

## Step 2: Create Physical Network Devices

Let's start with the network infrastructure - the foundation of your homelab.

### Create Router CI

**Via Web UI**:

1. Navigate to http://localhost:9080/pms/ci?@template=item
1. Fill in the form:
   - **Name**: `edgerouter-x`
   - **Type**: Network Device
   - **Status**: Active
   - **Location**: Network closet, shelf 1
   - **Criticality**: Very High (everything depends on it!)
   - **IP Address**: `192.168.1.1`
   - **Ports**: `5`
   - **Vendor**: Ubiquiti
   - **Description**: Primary gateway and router for homelab network
1. Click "Submit New Entry"

**Via CLI**:

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="edgerouter-x" \
  type=2 \
  status=5 \
  location="Network closet, shelf 1" \
  criticality=5 \
  ip_address="192.168.1.1" \
  ports=5 \
  vendor="Ubiquiti"
```

### Create Core Switch

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="core-switch-us24" \
  type=2 \
  status=5 \
  location="Network closet, shelf 2" \
  criticality=5 \
  ip_address="192.168.1.2" \
  ports=24 \
  vendor="Ubiquiti"
```

### Create PoE Switch

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="poe-switch-us8" \
  type=2 \
  status=5 \
  location="Network closet, shelf 2" \
  criticality=4 \
  ip_address="192.168.1.3" \
  ports=8 \
  vendor="Ubiquiti"
```

### Verify Network Devices

```bash
cd tracker
uv run roundup-admin -i . find ci type=2  # Network Devices
```

You should see 3 CIs: router, core switch, and PoE switch.

## Step 3: Create Storage Infrastructure

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="nas-ds920plus" \
  type=3 \
  status=5 \
  location="Server rack, unit 1" \
  criticality=5 \
  ip_address="192.168.1.10" \
  capacity_gb=32000 \
  vendor="Synology"
```

## Step 4: Create Physical Servers

### Hypervisor Server

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="hypervisor-dell-r720" \
  type=1 \
  status=5 \
  location="Server rack, unit 5-7" \
  criticality=5 \
  ip_address="192.168.1.20" \
  cpu_cores=24 \
  ram_gb=128 \
  os="Proxmox VE 8.1"
```

### Docker Host Server

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="docker-host-ml350" \
  type=1 \
  status=5 \
  location="Server rack, unit 10-12" \
  criticality=4 \
  ip_address="192.168.1.30" \
  cpu_cores=16 \
  ram_gb=64 \
  os="Ubuntu 24.04 LTS"
```

## Step 5: Create Virtual Machines

### Database VM

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="db-server-vm" \
  type=6 \
  status=5 \
  location="Virtual - Proxmox" \
  criticality=5 \
  ip_address="192.168.1.50" \
  cpu_cores=4 \
  ram_gb=16 \
  os="Ubuntu 24.04 LTS"
```

### Web Server VM

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="web-server-vm" \
  type=6 \
  status=5 \
  location="Virtual - Proxmox" \
  criticality=4 \
  ip_address="192.168.1.51" \
  cpu_cores=2 \
  ram_gb=8 \
  os="Ubuntu 24.04 LTS"
```

### Monitoring VM

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="monitoring-vm" \
  type=6 \
  status=5 \
  location="Virtual - Proxmox" \
  criticality=3 \
  ip_address="192.168.1.52" \
  cpu_cores=2 \
  ram_gb=4 \
  os="Debian 12"
```

## Step 6: Create Software and Services

### PostgreSQL Service

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="postgresql-service" \
  type=5 \
  status=5 \
  location="db-server-vm" \
  criticality=5 \
  version="16.1"
```

### Web Application

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="web-app-service" \
  type=5 \
  status=5 \
  location="web-server-vm" \
  criticality=4 \
  version="2.1.0"
```

### Prometheus Monitoring

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="prometheus-service" \
  type=5 \
  status=5 \
  location="monitoring-vm" \
  criticality=3 \
  version="2.48.0"
```

### Grafana Dashboard

```bash
cd tracker
uv run roundup-admin -i . create ci \
  name="grafana-service" \
  type=5 \
  status=5 \
  location="monitoring-vm" \
  criticality=3 \
  version="10.2.0"
```

## Step 7: Document Relationships

Now comes the crucial part - documenting how these components depend on each other.

### VM Hosting Relationships

```bash
cd tracker
# Database VM runs on hypervisor
uv run roundup-admin -i . create cirelationship \
  source_ci=7 \
  relationship_type=1 \
  target_ci=5

# Web server VM runs on hypervisor
uv run roundup-admin -i . create cirelationship \
  source_ci=8 \
  relationship_type=1 \
  target_ci=5

# Monitoring VM runs on hypervisor
uv run roundup-admin -i . create cirelationship \
  source_ci=9 \
  relationship_type=1 \
  target_ci=5
```

**What this means**: If the hypervisor goes down, all 3 VMs go down with it.

### Service Dependencies

```bash
cd tracker
# PostgreSQL service runs on DB VM
uv run roundup-admin -i . create cirelationship \
  source_ci=10 \
  relationship_type=1 \
  target_ci=7

# Web app runs on web server VM
uv run roundup-admin -i . create cirelationship \
  source_ci=11 \
  relationship_type=1 \
  target_ci=8

# Web app depends on PostgreSQL
uv run roundup-admin -i . create cirelationship \
  source_ci=11 \
  relationship_type=3 \
  target_ci=10

# Prometheus runs on monitoring VM
uv run roundup-admin -i . create cirelationship \
  source_ci=12 \
  relationship_type=1 \
  target_ci=9

# Grafana runs on monitoring VM
uv run roundup-admin -i . create cirelationship \
  source_ci=13 \
  relationship_type=1 \
  target_ci=9

# Grafana depends on Prometheus (data source)
uv run roundup-admin -i . create cirelationship \
  source_ci=13 \
  relationship_type=3 \
  target_ci=12
```

### Network Connectivity

```bash
cd tracker
# Servers connect to core switch
uv run roundup-admin -i . create cirelationship \
  source_ci=5 \
  relationship_type=5 \
  target_ci=2

uv run roundup-admin -i . create cirelationship \
  source_ci=6 \
  relationship_type=5 \
  target_ci=2

uv run roundup-admin -i . create cirelationship \
  source_ci=4 \
  relationship_type=5 \
  target_ci=2

# Core switch connects to router
uv run roundup-admin -i . create cirelationship \
  source_ci=2 \
  relationship_type=5 \
  target_ci=1
```

## Step 8: Verify Your CMDB

### View the Dashboard

Navigate to http://localhost:9080/pms/home?@template=dashboard

You should see:

- **Total CIs**: 13
- **By Type**: Servers (2), Network Devices (3), Storage (1), Services (4), VMs (3)
- **By Criticality**: Very High (5), High (1), Medium (4), Low (3)
- **Relationships**: 13 documented dependencies

### Query Relationships

```bash
cd tracker
# Find all VMs running on the hypervisor
uv run roundup-admin -i . find cirelationship source_ci=7,8,9 relationship_type=1

# Find all services depending on PostgreSQL
uv run roundup-admin -i . find cirelationship target_ci=10 relationship_type=3
```

## Step 9: Real-World Use Cases

### Use Case 1: Impact Analysis Before Change

**Scenario**: You need to reboot the hypervisor for kernel updates.

**Query**:

```bash
cd tracker
# Find all CIs running on hypervisor
uv run roundup-admin -i . find cirelationship target_ci=5 relationship_type=1
```

**Result**: 3 VMs will be affected (db-server-vm, web-server-vm, monitoring-vm)

**Follow-up**: What services run on those VMs?

```bash
cd tracker
# Find services on these VMs
uv run roundup-admin -i . find cirelationship target_ci=7,8,9 relationship_type=1
```

**Result**: 5 services will be down:

- PostgreSQL (critical!)
- Web app (critical!)
- Prometheus
- Grafana

**Decision**: Schedule maintenance window, notify users, ensure database backups are current.

### Use Case 2: Troubleshooting Network Outage

**Scenario**: Web app is unreachable.

**Troubleshooting Steps**:

1. **Check Web App CI**:

   ```bash
   cd tracker
   uv run roundup-admin -i . get ci11  # web-app-service
   ```

   Status: Active, Location: web-server-vm

1. **Check Dependencies**:

   ```bash
   cd tracker
   uv run roundup-admin -i . find cirelationship source_ci=11
   ```

   Depends on: web-server-vm, postgresql-service

1. **Check Web Server VM**:

   ```bash
   cd tracker
   uv run roundup-admin -i . get ci8  # web-server-vm
   ```

   Runs On: hypervisor-dell-r720

1. **Check Network Path**:

   ```bash
   cd tracker
   uv run roundup-admin -i . find cirelationship source_ci=5 relationship_type=5
   ```

   Connects To: core-switch-us24

1. **Conclusion**: Check hypervisor → core switch → router network path

### Use Case 3: Capacity Planning

**Scenario**: Adding new VM to hypervisor.

**Current Resource Usage**:

```bash
cd tracker
# Query hypervisor
uv run roundup-admin -i . get ci5

# Find current VMs
uv run roundup-admin -i . find cirelationship target_ci=5 relationship_type=1

# Check VM allocations
uv run roundup-admin -i . get ci7  # 4 cores, 16 GB
uv run roundup-admin -i . get ci8  # 2 cores, 8 GB
uv run roundup-admin -i . get ci9  # 2 cores, 4 GB
```

**Analysis**:

- Hypervisor: 24 cores, 128 GB RAM
- Allocated: 8 cores, 28 GB RAM
- Available: 16 cores, 100 GB RAM
- **Decision**: Plenty of capacity for new VM

## Step 10: Maintaining Your CMDB

### Daily/Weekly Tasks

**When Deploying New Infrastructure**:

1. Create CI in CMDB
1. Document relationships
1. Set appropriate criticality
1. Update IP address inventory

**When Making Changes**:

1. Create change request linking to affected CIs
1. Update CI attributes after change
1. Update relationships if topology changes

**When Decommissioning**:

1. Update CI status to "Retired"
1. Remove or archive relationships
1. Document retirement reason

### Monthly Review

```bash
cd tracker
# Review all active CIs
uv run roundup-admin -i . find ci status=5

# Check for undocumented relationships
# (CIs with no relationships are suspicious)
```

### Quarterly Audit

1. Verify CI attributes are current
1. Confirm relationship accuracy
1. Update criticality levels if needed
1. Archive retired CIs older than 90 days

### Automation Tips

**Inventory Script**:

```bash
#!/bin/bash
# sync-inventory.sh - Update CMDB from infrastructure

# Example: Update IP addresses from DHCP leases
for host in $(awk '{print $2,$3}' /var/lib/dhcp/dhcpd.leases); do
  hostname=$(echo $host | cut -d' ' -f1)
  ip=$(echo $host | cut -d' ' -f2)

  cd tracker
  uv run roundup-admin -i . find ci name=$hostname | while read ci_id; do
    uv run roundup-admin -i . set ci$ci_id ip_address=$ip
  done
done
```

**Monitoring Integration**:

```bash
# When Prometheus detects new host, create CI automatically
curl -X POST http://localhost:9080/pms/rest/data/ci \
  -u admin:admin \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$hostname\",
    \"type\": \"1\",
    \"status\": \"5\",
    \"ip_address\": \"$ip\"
  }"
```

## Summary

You've now built a complete CMDB for your homelab! You've learned to:

✅ Create CIs for physical and virtual infrastructure
✅ Document relationships between components
✅ Use the CMDB for impact analysis
✅ Query the CMDB for troubleshooting
✅ Plan capacity using CMDB data
✅ Maintain your CMDB over time

## Next Steps

- **How-to**: [Documenting Infrastructure Dependencies](../howto/documenting-infrastructure-dependencies.md)
- **Reference**: [CMDB Schema](../reference/cmdb-schema.md)
- **Reference**: [CI Relationship Types](../reference/ci-relationship-types.md)
- **Explanation**: [Why Configuration Management Matters](../explanation/why-configuration-management.md)

## Common Questions

**Q: Do I need to document every cable and power supply?**

A: No. Focus on actionable information. Document what helps you troubleshoot and make decisions. Physical details like rack units and cable labels can go in CI descriptions if needed.

**Q: How do I keep the CMDB in sync with reality?**

A: Integrate CMDB updates into your deployment workflow. When you deploy a VM, create the CI. When you decommission a server, retire the CI. Make it a habit, not an afterthought.

**Q: What if I have multiple sites (home, office, colo)?**

A: Use the `location` field consistently. For example:

- "Home Lab - Rack 1"
- "Office - Network Closet"
- "Colo - Cage 42, Rack 3"

**Q: Should I track development/test environments?**

A: Yes, but set criticality appropriately. Production CIs are High/Very High. Development CIs are Low/Very Low. This helps prioritize incident response.

**Q: How detailed should relationship documentation be?**

A: Document dependencies that matter for troubleshooting and impact analysis. At minimum:

- VM → Physical host
- Service → VM/container
- Critical service dependencies
- Network connectivity for servers

## Troubleshooting

### CI IDs Don't Match Tutorial

CI IDs are auto-generated. If your IDs differ from this tutorial, use `find` to get the correct IDs:

```bash
cd tracker
uv run roundup-admin -i . find ci name=hypervisor-dell-r720
# Use the returned ID in subsequent commands
```

### Relationship Creation Fails

Ensure source and target CIs exist:

```bash
cd tracker
uv run roundup-admin -i . get ci5
uv run roundup-admin -i . get ci7
```

### Can't Find CIs in Web UI

Ensure database is reindexed:

```bash
cd tracker
uv run roundup-admin -i . reindex ci
```

Restart the server:

```bash
pkill -f roundup-server && sleep 2
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```
