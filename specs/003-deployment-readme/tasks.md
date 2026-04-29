# Implementation Tasks: Deployment README Documentation

**Feature**: Deployment README Documentation  
**Branch**: `003-deployment-readme`  
**Total Tasks**: 28  
**Execution Strategy**: MVP scope (US1 + US2 + US3 = core deployment guides), then add US4 (troubleshooting) for full feature

---

## Dependencies & Execution Order

### Story Dependencies

```
US1 (Raspberry Pi) [P1] ─┐
US2 (PC) [P1]         ├─→ (Independent, can run in parallel)
US3 (Docker) [P1]     ─┘
                        ↓
US4 (Troubleshooting) [P2] (Depends on other 3 for reference commands)
```

### Parallel Execution

- **Phase 2 (Foundational)**: All tasks can run in parallel [P]
- **Phase 3 (US1)**: T009-T012 independent, can parallelize [P]
- **Phase 4 (US2)**: T013-T016 independent, can parallelize [P]
- **Phase 5 (US3)**: T017-T020 independent, can parallelize [P]
- **Phase 6 (US4)**: Depends on completion of US1-US3, tasks T021-T027 can parallelize [P]

---

## Phase 1: Setup

### Goal
Initialize documentation structure and environment.

### Independent Test Criteria
- README.md exists in repository root
- Spec and plan documents complete and accessible
- Documentation structure created per plan.md

### Tasks

- [x] T001 Create README.md with table of contents stub in repository root
- [x] T002 Create .docs/examples/ directory for command examples and test scenarios
- [x] T003 Create architecture ASCII diagram template in docs/ARCHITECTURE.md
- [x] T004 Verify existing documentation files (DOCKER.md, DEPLOYMENT.md, CI-CD.md) are intact

---

## Phase 2: Foundational (Blocking Prerequisites)

### Goal
Prepare shared content and validate existing information.

### Independent Test Criteria
- Header/introduction section complete
- Architecture overview documented
- Environment variables documented with explanations

### Tasks

- [x] T005 [P] Write README header and project description (overview, key features) in README.md lines 1-20
- [x] T006 [P] Write Prerequisites section (Docker v20.10+, Python 3.10+, git) in README.md
- [x] T007 [P] Create Environment Variables reference table in README.md with all vars from .env.example files
- [x] T008 [P] Write Architecture Overview section with ASCII diagram in README.md

---

## Phase 3: User Story 1 - Raspberry Pi Deployment Guide [P1]

### Story Goal
Raspberry Pi で Power-On WOL サービスをデプロイしたい開発者・運用者が、README から完全なセットアップ手順を確認できるようにする。

### Acceptance Criteria (from spec.md)
1. README の「Raspberry Pi デプロイ」セクションを読んで、step-by-step でセットアップできる手順が明確に記載されている
2. 初心者ユーザーが README の手順に従って 10分以内に WOL サービスが起動できる
3. セットアップ完了後、Web UI にアクセス、ポート 5000 で正常に動作している

### Independent Test Criteria
- Raspberry Pi deployment section present and complete
- All commands are copy-pasteable and tested
- Expected output for each step documented
- Health check endpoint documented

### Tasks

- [x] T009 [P] [US1] Write Raspberry Pi deployment section header and prerequisites in README.md
- [x] T010 [P] [US1] Document git clone and directory structure setup steps in README.md
- [x] T011 [P] [US1] Document .env file configuration with PC_ADDRESS, WOL_TARGET_MAC, port settings in README.md
- [x] T012 [P] [US1] Document docker compose up and health check validation steps in README.md

---

## Phase 4: User Story 2 - PC Deployment Guide [P1]

### Story Goal
Windows/Linux PC で Power-On 電源管理 API をデプロイしたい開発者が、README からセットアップ手順を確認できるようにする。

### Acceptance Criteria (from spec.md)
1. README の「PC デプロイ」セクションを読んで、step-by-step でセットアップできる手順が明確に記載されている
2. 初心者ユーザーが README の手順に従って 5分以内に API サーバーが起動できる
3. セットアップ完了後、API の health check endpoint にアクセス、正常に応答している

### Independent Test Criteria
- PC deployment section present and complete
- Platform-specific variations noted (Linux, macOS, Windows)
- All commands tested and working
- Health check validation steps clear

### Tasks

- [x] T013 [P] [US2] Write PC deployment section header and prerequisites in README.md
- [x] T014 [P] [US2] Document git clone and repository setup for PC component in README.md
- [x] T015 [P] [US2] Document .env file configuration with port, shutdown timeout, host settings in README.md
- [x] T016 [P] [US2] Document docker compose up and health check validation for PC API in README.md

---

## Phase 5: User Story 3 - Docker Deployment Option [P1]

### Story Goal
Docker を使った簡単デプロイを希望するユーザーが、README からコンテナ化デプロイの手順を確認できるようにする。

### Acceptance Criteria (from spec.md)
1. README の「Docker デプロイ」セクションを読んで、`docker compose up -d` で即座にデプロイできる手順が記載されている
2. Docker インストール済み環境で Docker セクションの手順に従い、2分以内に両サービスが起動できる

### Independent Test Criteria
- Docker quick-start section present (5 minutes or less)
- Single docker compose command documented
- Expected output shown
- Both rpi-wol and pc-power services in compose file referenced

### Tasks

- [x] T017 [P] [US3] Write Docker Quick Start section (single command deployment) in README.md
- [x] T018 [P] [US3] Document docker compose up command with environment variable substitution in README.md
- [x] T019 [P] [US3] Document how to access both services (Web UI on 5000, API on 5001) in README.md
- [x] T020 [P] [US3] Write Docker service verification steps (curl health endpoints) in README.md

---

## Phase 6: User Story 4 - Troubleshooting Guide [P2]

### Story Goal
デプロイ中に問題が発生したユーザーが、README のトラブルシューティング章で解決方法を見つけられるようにする。

### Acceptance Criteria (from spec.md)
1. README のトラブルシューティングセクションに、ポート競合、権限エラー、ネットワーク接続等の一般的な問題への対応が記載されている
2. デプロイ中にエラー発生時、README のトラブルシューティングを確認して問題が解決できるか手がかりが得られる

### Independent Test Criteria
- Troubleshooting section covers 80% of common deployment failures
- Each issue includes symptom, diagnosis, and solution
- Cross-references to logs and health checks
- Platform-specific gotchas documented

### Tasks

- [x] T021 [P] [US4] Write Troubleshooting section header and common issues overview in README.md
- [x] T022 [P] [US4] Document port conflict diagnosis and resolution (5000/5001 already in use) in README.md
- [x] T023 [P] [US4] Document permission error diagnosis and resolution (docker daemon, file ownership) in README.md
- [x] T024 [P] [US4] Document network connectivity diagnosis (PC_ADDRESS unreachable, SSH keys) in README.md
- [x] T025 [P] [US4] Document Docker-specific issues (image pull failures, disk space, daemon errors) in README.md
- [x] T026 [P] [US4] Document health check endpoints and log inspection procedures in README.md
- [x] T027 [P] [US4] Document performance issues and common gotchas (Raspberry Pi SD card, system load) in README.md

---

## Phase 7: Polish & Cross-Cutting Concerns

### Goal
Add finishing touches, validate, and prepare for publication.

### Tasks

- [x] T028 Validate all command samples are executable and tested, update README.md with verified examples
- [x] T029 Create .docs/examples/ folder with tested shell scripts for each deployment scenario
- [x] T030 Verify README links to existing docs (DOCKER.md, DEPLOYMENT.md, CI-CD.md) are correct
- [x] T031 Add Table of Contents with proper anchor links at top of README.md
- [x] T032 Proofread README for clarity, consistency, and tone for non-technical users
- [x] T033 Final validation: README satisfies all 10 functional requirements from spec.md
- [x] T034 Final validation: README satisfies all 5 success criteria from spec.md

---

## Implementation Strategy

### MVP Scope (Recommended First Iteration)
**Tasks**: T001-T020 (~2 hours)
- ✅ Phase 1: Setup
- ✅ Phase 2: Foundational (shared content)
- ✅ Phase 3: US1 (Raspberry Pi)
- ✅ Phase 4: US2 (PC)
- ✅ Phase 5: US3 (Docker)

**Result**: Beginners can deploy all three configurations with clear step-by-step guides.

### Full Scope (Second Iteration)
**Tasks**: T021-T034 (~1 hour)
- ✅ Phase 6: US4 (Troubleshooting)
- ✅ Phase 7: Polish & validation

**Result**: Complete deployment documentation with comprehensive troubleshooting and examples.

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 34 |
| MVP Tasks | 20 |
| Setup Phase | 4 tasks |
| Foundational Phase | 4 tasks |
| US1 (Raspberry Pi) [P1] | 4 tasks |
| US2 (PC) [P1] | 4 tasks |
| US3 (Docker) [P1] | 4 tasks |
| US4 (Troubleshooting) [P2] | 7 tasks |
| Polish Phase | 7 tasks |
| Parallelizable Tasks | 25 (marked [P]) |
| Independent Test Criteria | 4 (one per phase) |
| Estimated Time (MVP) | 2-3 hours |
| Estimated Time (Full) | 3-4 hours |

---

## Coverage Mapping to Requirements

### Functional Requirements → Tasks

| Requirement | Task(s) | Coverage |
|-------------|---------|----------|
| FR-001: Raspberry Pi deployment guide | T009-T012 | ✅ |
| FR-002: PC deployment guide | T013-T016 | ✅ |
| FR-003: Docker deployment option | T017-T020 | ✅ |
| FR-004: Prerequisites documentation | T006 | ✅ |
| FR-005: Network configuration details | T007, T011, T015, T019 | ✅ |
| FR-006: Troubleshooting section | T021-T027 | ✅ |
| FR-007: Quick-start section | T017-T020, T028 | ✅ |
| FR-008: Architecture diagram/text | T008, T003 | ✅ |
| FR-009: Environment variables list | T007 | ✅ |
| FR-010: Table of Contents | T031 | ✅ |

### Success Criteria → Validation

| Success Criterion | Validation Task | Expected Outcome |
|------------------|-----------------|------------------|
| SC-001: 15-min deploy for beginners | T028 + T032 | Commands tested, timing validated |
| SC-002: 80% troubleshooting coverage | T021-T027 | 7 common issues documented |
| SC-003: 5-min quick-start | T017-T020 | Single command, clear validation |
| SC-004: Command samples executable | T028 + T029 | All examples tested in .docs/ |
| SC-005: No additional questions needed | T032 + T033 | Comprehensive coverage confirmed |

