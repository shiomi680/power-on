# Implementation Plan: Deployment README Documentation

**Branch**: `003-deployment-readme` | **Date**: 2026-04-29 | **Spec**: [specs/003-deployment-readme/spec.md](spec.md)
**Input**: Feature specification from `/specs/003-deployment-readme/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

README に Raspberry Pi、PC、Docker デプロイ手順を段階的に記載し、初心者ユーザーが 15 分以内でシステムをセットアップできる包括的なデプロイメントガイドを提供します。トラブルシューティング章を追加して、よくある問題への対応方法も明記します。技術的には、既存のドキュメント（DOCKER.md, DEPLOYMENT.md, CI-CD.md）と重複しない形で、快速スタートと段階的な詳細説明を両立させます。

## Technical Context

**Language/Version**: Markdown documentation for GitHub  
**Primary Dependencies**: N/A (documentation only, no code dependencies)  
**Storage**: N/A  
**Testing**: Content validation through command sample execution (SC-004 acceptance criteria)  
**Target Platform**: GitHub repository (public documentation)  
**Project Type**: Documentation/Deployment guides  
**Performance Goals**: Beginners can deploy in 15 minutes (SC-001), quick-start in 5 minutes (SC-003)  
**Constraints**: Clarity for non-technical users, complete command examples, no implementation-specific details  
**Scale/Scope**: Single README.md file with major sections (TOC, quick-start, prerequisites, architecture, deployment guides, environment variables, troubleshooting)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. 日本語優先 | ✅ PASS | README is English (GitHub standard), but spec and planning docs in Japanese. Documentation content honors clarity principle. |
| II. Library-First | ⚠ N/A | Documentation for existing libraries, not creating new libraries. |
| III. CLI Interface | ⚠ N/A | Documentation task, not CLI interface creation. |
| IV. テスト優先 | ✅ PASS | Spec includes SC-004: "ユーザーがデプロイ手順について追加で質問する必要がない（README で十分）" - validates through user testing. |
| V. 統合テスト重視 | ✅ PASS | Command samples in README will be validated for functional correctness (SC-004). |

**Result**: PASS - Documentation task with no constitution violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/003-deployment-readme/
├── plan.md              # This file
├── research.md          # Phase 0: README structure options, best practices for deployment documentation
├── data-model.md        # Phase 1: Content structure and section dependencies
├── quickstart.md        # Phase 1: Deployment example scenarios
├── contracts/           # Phase 1: README content contract (sections, format)
└── tasks.md             # Phase 2: Documentation writing tasks (created by /speckit-tasks)
```

### Deliverable (repository root)

```text
README.md                # Main deployment documentation (NEW/UPDATED)
├── Table of Contents
├── Quick Start (5 minutes)
├── Prerequisites & System Requirements
├── Architecture Overview (text + diagram reference)
├── Deployment Guides
│   ├── Raspberry Pi WOL Service
│   ├── PC Power Control API
│   └── Docker Deployment (both services)
├── Environment Variables Reference
├── Troubleshooting Guide
│   ├── Port conflicts
│   ├── Permission errors
│   ├── Network connectivity
│   ├── Docker issues
│   └── API health checks
└── Additional Resources (links to DOCKER.md, CI-CD.md, etc.)
```

**Structure Decision**: Single README.md file serving as the primary entry point for new users. Existing docs (docs/DOCKER.md, docs/DEPLOYMENT.md, docs/CI-CD.md) remain as reference material. README provides beginner-friendly step-by-step instructions; docs/ provides technical deep-dives.

## Phase 0: Research

### Key Questions to Resolve

1. **README Structure & Narrative Flow**
   - Research: GitHub README best practices for multi-platform deployment documentation
   - Research: Pyramid principle for organizing deployment content (quick-start → detailed guides)
   - Decision: Top-level quick-start wins for time-pressed users; platform-specific sections follow

2. **Platform-Specific Instructions Coverage**
   - Research: Command differences between Linux/macOS/Windows for Python/Docker setup
   - Research: Network configuration differences for Raspberry Pi vs desktop environments
   - Decision: Provide platform detection guidance; document primary path (Linux/macOS) with Windows notes

3. **Troubleshooting Depth & Coverage**
   - Research: Common deployment failure modes for Flask apps + Docker + Raspberry Pi
   - Research: Port conflict diagnosis, permission error patterns, network debugging techniques
   - Decision: Focus on 80% of common issues (port 5000/5001 conflicts, missing .env, SSH key issues)

4. **Command Sample Validation Strategy**
   - Research: How to document commands that work across different shell environments
   - Research: Environment variable syntax for .env files across platforms
   - Decision: Use `docker compose` (V2) syntax; provide `.env.example` files with comments; test all samples before README publication

5. **Diagram & Visual Content**
   - Research: ASCII diagram vs external image for README deployment architecture
   - Decision: Use ASCII diagram in README for no external dependencies; reference existing architecture docs

## Phase 1: Design

### README Content Model

**Header Section**
- Feature description: What is Power-On system?
- Links to existing docs, repos, deployment status

**Table of Contents (auto-generated)**
- Anchor links to all major sections

**Quick Start Section (5 minutes)**
- Single-command deployment using docker compose
- Expected output and success indicators
- One success path only (Docker)

**Prerequisites**
- System requirements: OS, RAM, disk space
- Software requirements: Docker version, Python version (if native)
- Network requirements: ports, firewall rules
- Hardware requirements: for Raspberry Pi vs PC deployments

**Architecture Overview**
- Text description: Components (rpi-wol, pc-power, Docker registry)
- Relationships and communication flows
- Reference to diagram location

**Deployment Guides (4 options)**
- Native Raspberry Pi (with systemd/cron)
- Native PC (with systemd/Windows scheduled task notes)
- Docker single-command
- Docker Compose with environment configuration

**Environment Variables**
- Table format with variable name, purpose, default, example
- .env file template with all variables
- Platform-specific variations noted

**Troubleshooting**
- Organized by symptom (not cause)
- Each entry: Symptom → diagnosis → solution
- Links to health check endpoints and log files

**Appendices**
- Glossary: WOL, MAC address, broadcast IP
- Related documentation: DOCKER.md, DEPLOYMENT.md, CI-CD.md
- FAQ: Common questions beyond troubleshooting

### Content Contracts

**Quick Start Contract**
- 5 minutes to working system, one command
- No prerequisites other than Docker installed
- Clear success criteria (API responds, Web UI loads)

**Deployment Guide Contract**
- Step-by-step instructions for each platform
- All commands copy-pasteable
- Error messages and expected output shown
- ~5-10 minutes per guide

**Troubleshooting Contract**
- 80% of common issues covered
- Diagnostic steps for each issue
- Links to logs and health check endpoints

**Command Sample Contract**
- All sample commands tested and working
- Environment variables marked with ${VAR_NAME}
- Platform-specific variations noted with [Linux/macOS/Windows] tags

### Quickstart Scenarios

1. **Developer Quick-Start (5 min)**
   - Clone repo → docker compose up → open http://localhost:5000
   - Shows both services running

2. **Raspberry Pi Deployment (10-15 min)**
   - git clone → .env setup → docker compose up
   - Verify with curl to health endpoints
   - Test WOL with sample command

3. **PC Deployment (10-15 min)**
   - git clone → .env setup with PC_ADDRESS → docker compose up
   - Verify API health
   - Test shutdown endpoint

4. **Troubleshooting Walkthrough**
   - Port already in use → change port in docker-compose.yml
   - Cannot connect to PC → check PC_ADDRESS and network
   - Docker image download fails → check internet and docker daemon

## Complexity Tracking

No constitution violations identified. This is a documentation task with clear success criteria defined in spec.md.
