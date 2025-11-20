<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How-to: Verifying PMS Releases

This guide explains how to verify the authenticity and integrity of Pasture Management System (PMS) releases using SLSA provenance attestations.

## Overview

PMS releases include cryptographically signed SLSA provenance attestations that prove:

- **Authenticity**: The release was built by the official PMS GitHub Actions workflow
- **Integrity**: The release artifacts have not been tampered with since build time
- **Traceability**: The exact source code commit and build process used

**SLSA Level**: Level 3 (exceeds v1.0.0 target of Level 1)

## Quick Verification

For most users, the simplest verification is checking the GitHub release page:

1. Navigate to: https://github.com/jrjsmrtn/pasture-management-system/releases
1. Click on the desired release (e.g., `v1.0.0`)
1. Verify the release shows:
   - ✅ **Verified** badge (GitHub verifies SLSA provenance automatically)
   - Source code archive (`.tar.gz`)
   - SLSA provenance file (`.intoto.jsonl`)
   - Checksum file (`checksums.txt`)

**If the "Verified" badge is present, GitHub has already validated the SLSA provenance.**

## Manual Verification (Advanced)

For security-conscious users who want to verify provenance independently:

### Prerequisites

Install the SLSA verifier tool:

```bash
# macOS with Homebrew
brew install slsa-verifier

# Or download from GitHub releases
# https://github.com/slsa-framework/slsa-verifier/releases
```

### Step 1: Download Release Artifacts

Download from the GitHub release page:

- Source archive: `pasture-management-system-v1.0.0.tar.gz`
- Provenance attestation: `pasture-management-system-v1.0.0.tar.gz.intoto.jsonl`

Or using curl:

```bash
VERSION="v1.0.0"
REPO="jrjsmrtn/pasture-management-system"

# Download source archive
curl -LO "https://github.com/${REPO}/releases/download/${VERSION}/pasture-management-system-${VERSION}.tar.gz"

# Download provenance
curl -LO "https://github.com/${REPO}/releases/download/${VERSION}/pasture-management-system-${VERSION}.tar.gz.intoto.jsonl"
```

### Step 2: Verify Provenance

Use the SLSA verifier to validate the provenance:

```bash
slsa-verifier verify-artifact \
  --provenance-path pasture-management-system-v1.0.0.tar.gz.intoto.jsonl \
  --source-uri github.com/jrjsmrtn/pasture-management-system \
  pasture-management-system-v1.0.0.tar.gz
```

**Expected Output** (verification successful):

```
Verified signature against tlog entry index 12345678 at URL: https://rekor.sigstore.dev/api/v1/log/entries/...
Verified build using builder "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@refs/tags/v2.1.0" at commit abc123def456...
Verifying artifact pasture-management-system-v1.0.0.tar.gz: PASSED

PASSED: Verified SLSA provenance
```

**If verification fails**, do NOT use the artifact - it may have been tampered with.

### Step 3: Verify Checksum (Optional)

Additionally verify the SHA256 checksum:

```bash
# Check SHA256 matches the checksums.txt file
sha256sum pasture-management-system-v1.0.0.tar.gz

# Compare with checksums.txt from the release
curl -s "https://github.com/jrjsmrtn/pasture-management-system/releases/download/v1.0.0/checksums.txt"
```

## What is SLSA Provenance?

**SLSA** (Supply-chain Levels for Software Artifacts) is a framework for ensuring software supply chain integrity.

**Provenance** is metadata about how an artifact was built, including:

- **Build Platform**: GitHub Actions (trusted build service)
- **Source Repository**: github.com/jrjsmrtn/pasture-management-system
- **Source Commit**: Exact git commit SHA
- **Build Steps**: Commands executed during build
- **Builder Identity**: Official SLSA generator workflow
- **Timestamp**: When the build occurred

**SLSA Level 3** (PMS v1.0.0) provides:

1. ✅ Fully automated, scripted build
1. ✅ Signed provenance attestation
1. ✅ Provenance includes all build inputs
1. ✅ Hardened build platform (GitHub Actions)
1. ✅ Non-falsifiable provenance (Sigstore transparency log)

## Understanding Verification Output

### Provenance Signature Verification

```
Verified signature against tlog entry index 12345678
```

- **What it means**: The provenance was signed by GitHub Actions using Sigstore
- **Why it matters**: Proves the provenance wasn't created by an attacker
- **Transparency log**: Public record at https://rekor.sigstore.dev/

### Builder Verification

```
Verified build using builder "slsa-github-generator"
```

- **What it means**: The artifact was built by the official SLSA generator
- **Why it matters**: Confirms the build happened on GitHub Actions, not a compromised machine

### Artifact Hash Verification

```
Verifying artifact: PASSED
```

- **What it means**: The artifact's SHA256 hash matches the provenance
- **Why it matters**: Proves the file wasn't modified after the build

## Common Verification Scenarios

### Scenario 1: Installing from GitHub Release

**Risk**: Low - GitHub validates provenance automatically

**Verification Steps**:

1. Check for "Verified" badge on release page
1. Download source archive
1. Optional: Run `slsa-verifier` for extra assurance

### Scenario 2: Installing from Third-Party Mirror

**Risk**: Medium - Mirror could serve tampered artifacts

**Verification Steps** (required):

1. Download provenance from official GitHub release
1. Download artifact from mirror
1. **Always** run `slsa-verifier` before using

### Scenario 3: Automated Deployment Pipeline

**Risk**: Medium - Compromise could affect multiple systems

**Verification Steps** (required):

1. Integrate `slsa-verifier` into deployment automation
1. Fail deployment if verification fails
1. Log verification results for audit trail

Example CI/CD integration:

```yaml
- name: Download and verify PMS release
  run: |
    VERSION="v1.0.0"
    curl -LO "https://github.com/jrjsmrtn/pasture-management-system/releases/download/${VERSION}/pasture-management-system-${VERSION}.tar.gz"
    curl -LO "https://github.com/jrjsmrtn/pasture-management-system/releases/download/${VERSION}/pasture-management-system-${VERSION}.tar.gz.intoto.jsonl"

    slsa-verifier verify-artifact \
      --provenance-path pasture-management-system-${VERSION}.tar.gz.intoto.jsonl \
      --source-uri github.com/jrjsmrtn/pasture-management-system \
      pasture-management-system-${VERSION}.tar.gz || exit 1

    echo "✅ SLSA provenance verified"
```

## Troubleshooting Verification

### Error: "failed to verify signature"

**Cause**: Provenance file is corrupted or not authentic

**Solution**:

1. Re-download the `.intoto.jsonl` file from GitHub
1. Verify you're using the official repository URL
1. Check network connection wasn't compromised (use HTTPS)

### Error: "source commit mismatch"

**Cause**: You specified the wrong git commit or tag

**Solution**:

- Ensure you're verifying against the correct release tag (e.g., `v1.0.0`)
- Check the release page for the correct commit SHA

### Error: "artifact hash mismatch"

**Cause**: The artifact file was modified after download

**Solution**:

1. **Stop using this artifact** - it may be compromised
1. Delete the downloaded file
1. Re-download from official GitHub release
1. Run verification again
1. If still fails, report to security@project (see Security Policy)

## Security Best Practices

### For Homelab Deployments

1. **Always verify production releases**:

   - Development/testing: GitHub "Verified" badge sufficient
   - Production: Run `slsa-verifier` manually

1. **Store provenance for audit**:

   ```bash
   mkdir -p ~/pms-releases/v1.0.0/
   mv *.intoto.jsonl ~/pms-releases/v1.0.0/
   ```

1. **Document verification in deployment log**:

   ```bash
   echo "$(date): Verified PMS v1.0.0 SLSA provenance" >> ~/pms-deploy.log
   ```

### For Production Environments

1. **Automate verification**:

   - Integrate `slsa-verifier` into CI/CD pipeline
   - Fail deployments if verification fails
   - Alert on verification failures

1. **Maintain verification audit trail**:

   - Log all verification attempts
   - Include commit SHA, timestamp, result
   - Retain logs for compliance/forensics

1. **Review provenance contents**:

   ```bash
   cat pasture-management-system-v1.0.0.tar.gz.intoto.jsonl | jq
   ```

   - Verify expected commit SHA
   - Check build timestamp makes sense
   - Confirm builder is official SLSA generator

## Provenance File Format

SLSA provenance is stored in in-toto format (`.intoto.jsonl`):

```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "subject": [
    {
      "name": "pasture-management-system-v1.0.0.tar.gz",
      "digest": {
        "sha256": "abc123..."
      }
    }
  ],
  "predicate": {
    "builder": {
      "id": "https://github.com/slsa-framework/slsa-github-generator"
    },
    "buildType": "https://github.com/slsa-framework/slsa-github-generator/generic@v1",
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/jrjsmrtn/pasture-management-system@refs/tags/v1.0.0",
        "digest": {
          "sha1": "def456..."
        }
      }
    },
    "materials": [...],
    "metadata": {
      "buildStartedOn": "2025-11-20T10:00:00Z",
      "buildFinishedOn": "2025-11-20T10:05:00Z"
    }
  }
}
```

## Future SLSA Levels

**v1.0.0**: SLSA Level 3 ✅

**v1.1.0+**: Potential improvements:

- SLSA Level 4: Two-party review requirement
- Signed commits (GPG/SSH signatures)
- Build reproducibility (bit-for-bit identical builds)
- Additional artifact types (Docker images, Python wheels)

## Related Documentation

- [Security Considerations](../reference/security-considerations.md) - Security features and audit results
- [Deployment Guide](deployment-guide.md) - Production deployment procedures
- [Installation Guide](installation-guide.md) - Installation from verified releases
- [ADR-0004](../adr/0004-adopt-mit-license-and-slsa-level-1.md) - SLSA adoption decision

## External Resources

- **SLSA Framework**: https://slsa.dev/
- **SLSA Verifier Tool**: https://github.com/slsa-framework/slsa-verifier
- **SLSA GitHub Generator**: https://github.com/slsa-framework/slsa-github-generator
- **Sigstore**: https://www.sigstore.dev/ (transparency log)
- **in-toto**: https://in-toto.io/ (attestation format)

## Reporting Verification Issues

If you encounter provenance verification failures or suspect a compromised release:

1. **Do not use the artifact**
1. **Report immediately**:
   - GitHub Security Advisories: https://github.com/jrjsmrtn/pasture-management-system/security/advisories
   - Email: security@project (see SECURITY.md)
1. **Include in report**:
   - Release version
   - Download source (GitHub/mirror/other)
   - Verification error message
   - SHA256 hash of downloaded file
   - Timestamp of download

## Summary

**For most users**:

- ✅ Download from official GitHub Releases page
- ✅ Look for "Verified" badge
- ✅ That's it! GitHub validates SLSA provenance automatically

**For production deployments**:

- ✅ Install `slsa-verifier` tool
- ✅ Run verification before installation
- ✅ Integrate into deployment automation
- ✅ Maintain verification audit logs

**SLSA Level 3 provenance provides strong assurance that PMS releases are authentic, unmodified, and built from trusted sources.**
