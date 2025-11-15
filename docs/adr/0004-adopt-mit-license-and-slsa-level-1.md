# ADR-0004: Adopt MIT License and SLSA Level 1

Date: 2025-11-15

## Status

Accepted

## Context

The Pasture Management System has dual objectives as both a functional homelab tool and an educational BDD demonstration platform. We need to choose an appropriate open-source license and establish supply chain security practices.

### License Considerations

The project serves multiple audiences:
- Homelab sysadmins seeking a practical ITIL-inspired tool
- Python developers learning BDD/Gherkin/Behave/Playwright
- Security-conscious users requiring transparent software practices

### Security Considerations

As a homelab management tool handling infrastructure data, supply chain security is important. SLSA (Supply-chain Levels for Software Artifacts) provides a framework for ensuring artifact integrity.

## Decision

### MIT License

We will use the **MIT License** for the Pasture Management System.

**Rationale**:
1. **Educational Accessibility**: Minimal restrictions maximize learning and adoption of BDD patterns
2. **Homelab Community Fit**: Permissive license aligns with DIY homelab culture
3. **Simplicity**: Easy to understand, low barrier for contributions
4. **Commercial Friendly**: Allows commercial use without copyleft requirements
5. **Roundup Compatibility**: Compatible with Roundup's Python-based permissive licensing

**Copyright**: Copyright (c) 2025 Georges Martin <jrjsmrtn@gmail.com>

**SPDX Headers**: All source files will include SPDX-License-Identifier headers:
```python
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT
```

### SLSA Level 1 Compliance

We will implement **SLSA Level 1** supply chain security practices.

**SLSA Level 1 Requirements**:
1. **Build Process**: Fully scripted/automated build process
2. **Provenance**: Generate provenance metadata for build artifacts
3. **Provenance Availability**: Make provenance available to consumers

**Implementation**:
- Automated builds via GitHub Actions
- Generate and publish SLSA provenance attestations
- Sign releases and artifacts
- Document build process completely
- Reproducible builds where possible

**Build Provenance Will Include**:
- Build platform (GitHub Actions)
- Build steps executed
- Source repository and commit SHA
- Builder identity
- Timestamp

## Consequences

### Positive

**License**:
- Maximum educational value and code reuse
- Simple contribution process
- Broad adoption potential
- Compatible with commercial and non-commercial use
- Clear legal standing

**SLSA Level 1**:
- Increased trust for homelab deployments
- Transparent build process
- Artifact integrity verification
- Foundation for future SLSA level progression
- Demonstrates security best practices

### Negative

**License**:
- No copyleft protection (derivatives can be closed-source)
- No explicit patent grant (unlike Apache 2.0)
- Trademark protection requires separate measures

**SLSA Level 1**:
- Additional CI/CD complexity
- Build time overhead for provenance generation
- Learning curve for supply chain security concepts
- Requires GitHub Actions integration

## Implementation

### Phase 1: License Application
- [x] Create LICENSE file with MIT License text
- [ ] Add SPDX headers to all source files
- [ ] Update README.md with license information
- [ ] Add license badge to README
- [ ] Document license in CLAUDE.md

### Phase 2: SLSA Level 1 Implementation (Sprint 1)
- [ ] Configure GitHub Actions for automated builds
- [ ] Install SLSA GitHub Actions generators
- [ ] Generate provenance for Python packages
- [ ] Publish provenance alongside releases
- [ ] Document build process
- [ ] Add SLSA badge to README

### Phase 3: Verification
- [ ] Verify SLSA provenance generation
- [ ] Test provenance verification workflow
- [ ] Document how users can verify artifacts
- [ ] Include verification in deployment documentation

## SPDX Header Format

All Python source files will include:
```python
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT
```

All Markdown documentation files will include:
```markdown
<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->
```

All YAML/configuration files will include:
```yaml
# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT
```

## SLSA Level 1 Resources

- **SLSA Framework**: https://slsa.dev/
- **GitHub SLSA Generator**: https://github.com/slsa-framework/slsa-github-generator
- **SLSA Provenance**: https://slsa.dev/provenance/

## Validation Criteria

**License**:
- [ ] LICENSE file present in repository root
- [ ] All source files have SPDX headers
- [ ] README documents license clearly
- [ ] GitHub repository shows license badge

**SLSA Level 1**:
- [ ] Builds fully automated via GitHub Actions
- [ ] Provenance generated for all releases
- [ ] Provenance publicly available and verifiable
- [ ] Build process documented
- [ ] Verification instructions provided

## Related Decisions

- ADR-0001: Record architecture decisions
- ADR-0002: Adopt development best practices (includes CI/CD)
- ADR-0003: Use Python with Roundup Issue Tracker toolkit

## Future Considerations

**SLSA Level 2+**: Future progression to higher SLSA levels:
- Level 2: Source and build platform integrity
- Level 3: Hardened builds, non-falsifiable provenance
- Level 4: Two-party review of all changes

**License Evolution**: Monitor for:
- Patent protection requirements (consider Apache 2.0)
- Trademark registration needs
- Contributor License Agreement (CLA) requirements
