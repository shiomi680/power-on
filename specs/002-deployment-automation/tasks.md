# Tasks: Deployment Automation (Docker + GitHub Actions)

**Input**: Design documents from `specs/002-deployment-automation/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story (US1, US2, US3) to enable independent implementation and testing.

**Tests**: No explicit test tasks - existing pytest framework (49 tests) runs automatically in GitHub Actions workflow.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Docker/GitHub environment verification

- [X] T001 Verify Docker and Docker Compose V2 are available in development environment
- [X] T002 Verify GitHub Actions is enabled in repository settings
- [X] T003 [P] Create base directory structure for deployment files (already exists: rpi-wol/, pc-power/, docs/, .github/workflows/)
- [X] T004 Verify existing Dockerfile structure matches deployment requirements (rpi-wol/Dockerfile, pc-power/Dockerfile)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Docker and CI/CD infrastructure that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Verify Raspberry Pi Dockerfile (rpi-wol/Dockerfile) has python:3.10-slim base image and required dependencies (libpcap for WOL)
- [X] T006 [P] Verify PC Dockerfile (pc-power/Dockerfile) has python:3.10-slim base image and system shutdown support
- [X] T007 Create .dockerignore in repository root to exclude build-irrelevant files (git, __pycache__, specs, .vscode)
- [X] T008 Verify GitHub Actions workflow file exists at .github/workflows/docker-publish.yml with matrix build strategy
- [X] T009 Verify GitHub Container Registry (ghcr.io) access is configured (GITHUB_TOKEN auto-generated)
- [X] T010 [P] Update .github/workflows/README.md to document trigger events and image tags

**Checkpoint**: Docker infrastructure ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Docker コンテナ化 (Priority: P1) 🎯 MVP

**Goal**: Create independent docker-compose.yml files for Raspberry Pi and PC, enabling simple `docker compose up -d` deployment on separate hardware

**Independent Test**: 
1. Run `cd rpi-wol && docker compose up -d` → Web UI accessible on port 5000
2. Run `cd pc-power && docker compose up -d` → API accessible on port 5001  
3. Both services show healthy status in `docker ps`

### Implementation for User Story 1

- [X] T011 [P] [US1] Create Raspberry Pi production docker-compose.yml (rpi-wol/docker-compose.yml) with service definition, port binding (5000), environment variables, health check
- [X] T012 [P] [US1] Create PC production docker-compose.yml (pc-power/docker-compose.yml) with service definition, port binding (5001), environment variables, health check
- [X] T013 [P] [US1] Create .env.example for rpi-wol with template values: FLASK_HOST, FLASK_PORT, PC_ADDRESS, PC_API_PORT, PC_API_TIMEOUT, WOL_TARGET_MAC, WOL_BROADCAST_IP, LOG_LEVEL
- [X] T014 [P] [US1] Create .env.example for pc-power with template values: FLASK_HOST, FLASK_PORT, SHUTDOWN_TIMEOUT, LOG_LEVEL
- [X] T015 [US1] Implement HEALTHCHECK in rpi-wol/Dockerfile to verify Web UI health (GET /api/health, interval 30s, timeout 5s, start-period 10s)
- [X] T016 [US1] Implement HEALTHCHECK in pc-power/Dockerfile to verify API health (GET /api/health, interval 30s, timeout 5s, start-period 10s)
- [X] T017 [P] [US1] Create root docker-compose.yml for development/testing with both services linked (rpi-wol and pc-power on same network, PC_ADDRESS=pc-power)
- [X] T018 [US1] Test US1 acceptance criteria: verify docker compose up works independently on each component

**Checkpoint**: Docker コンテナ化 (US1) complete - both rpi-wol and pc-power deployable independently with docker compose

---

## Phase 4: User Story 2 - CI/CD パイプライン (Priority: P1)

**Goal**: Implement GitHub Actions workflow that automatically runs tests, builds Docker images, and pushes them to ghcr.io on push/tag events

**Independent Test**:
1. Push code to main branch → GitHub Actions runs, tests pass, images built
2. Verify images in ghcr.io with correct tags (latest, main, sha-<commit>)
3. Push v1.0.0 tag → Images built with semantic version tags (v1.0.0, v1.0, v1)

### Implementation for User Story 2

- [X] T019 [P] [US2] Configure GitHub Actions workflow trigger events in docker-publish.yml: push (main, 001-pc-power-control branches), tags (v*), pull_request (main)
- [X] T020 [P] [US2] Implement matrix build strategy in docker-publish.yml to build rpi-wol and pc-power in parallel with correct component context (rpi-wol/Dockerfile, pc-power/Dockerfile)
- [X] T021 [P] [US2] Configure GitHub Actions test job to run pytest for both components (cd $component && pytest tests/ -v --tb=short)
- [X] T022 [P] [US2] Implement Docker Buildx setup in workflow (docker/setup-buildx-action@v3)
- [X] T023 [P] [US2] Configure GitHub Container Registry login in workflow using GITHUB_TOKEN secret
- [X] T024 [P] [US2] Implement metadata extraction in workflow using docker/metadata-action with tag rules:
  - ref (branch): main → latest + main, feature branches → branch-name-sha
  - semver (tags): v1.0.0 → v1.0.0 + v1.0 + v1
  - sha: all events → branch-sha-<commit>
- [X] T025 [P] [US2] Implement image build and push in workflow:
  - context: ./$component/
  - push: ${{ github.event_name != 'pull_request' }} (only push on push events, not PR)
  - cache-from: type=registry for registry cache
  - cache-to: type=registry,mode=max for layer caching
- [X] T026 [P] [US2] Test US2 acceptance criteria: push code, verify workflow runs, images appear in ghcr.io with correct tags
- [X] T027 [US2] Document workflow behavior in .github/workflows/README.md (triggers, tagging rules, images produced)

**Checkpoint**: CI/CD パイプライン (US2) complete - automated testing, building, and ghcr.io pushing on code changes

---

## Phase 5: User Story 3 - 本番環境デプロイの簡素化 (Priority: P2)

**Goal**: Enable simple one-command deployment in production by documenting environment setup and verifying health checks

**Independent Test**:
1. Copy .env.example → .env
2. Set PC_ADDRESS to target PC
3. Run `docker compose up -d`
4. Verify both containers reach healthy status in 30 seconds

### Implementation for User Story 3

- [X] T028 [P] [US3] Update docs/DOCKER.md with environment variable documentation for both components (table format: variable name, default, description)
- [X] T029 [P] [US3] Update docs/DEPLOYMENT.md with Raspberry Pi production deployment steps (clone, .env setup, docker compose up)
- [X] T030 [P] [US3] Update docs/DEPLOYMENT.md with PC production deployment steps (clone, .env setup, docker compose up, privilege notes)
- [X] T031 [P] [US3] Update docs/CI-CD.md with image pull and deployment instructions for both components (docker pull ghcr.io/... && docker compose up)
- [X] T032 [P] [US3] Create health check validation script or document manual verification: `docker ps` shows healthy status, `curl /api/health` on both ports
- [X] T033 [US3] Test US3 acceptance criteria: verify .env.example → .env workflow, docker compose up from empty state, health checks pass
- [X] T034 [US3] Update DEPLOYMENT.md troubleshooting section with common issues: port conflicts, permission errors, slow health checks

**Checkpoint**: 本番環境デプロイの簡素化 (US3) complete - operators can deploy with environment template and automatic health verification

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, logging, and operational readiness

- [X] T035 [P] Verify all existing unit tests (rpi-wol/tests/unit/, pc-power/tests/unit/) pass with `pytest -v`
- [X] T036 [P] Verify all existing contract tests (rpi-wol/tests/contract/, pc-power/tests/contract/) pass with `pytest -v`
- [X] T037 [P] Update project README.md with quick-start section for Docker deployment (development and production)
- [X] T038 Update quickstart.md with actual GitHub Container Registry username placeholders (docs/CI-CD.md examples)
- [X] T039 [P] Add logging output to both Dockerfiles (ensure Python logging outputs to stdout for docker logs)
- [X] T040 Verify .dockerignore excludes all unnecessary files (git/, __pycache__/, *.log, .env, specs/, .vscode/)
- [X] T041 [P] Test full CI/CD pipeline end-to-end: code push → tests pass → images built → ghcr.io push → manual docker pull and run
- [X] T042 Update git ignore to exclude .env and local docker artifacts if needed (.env, docker-compose.override.yml)

**Checkpoint**: All phases complete - system ready for production deployment

---

## Implementation Strategy

### MVP Scope (Phase 1-4)
- **What**: User Stories 1 (Docker コンテナ化) and 2 (CI/CD パイプライン) 
- **Why**: These are P1 priorities and deliver the core deployment capability
- **When**: Complete by end of Phase 4
- **Deliverable**: `docker compose up -d` works locally, GitHub Actions builds and pushes images to ghcr.io

### Incremental (Phase 5)
- **What**: User Story 3 (本番環境デプロイの簡素化)
- **Why**: Depends on US1 and US2 being complete
- **When**: Complete after US1/US2
- **Deliverable**: Production deployment guide, health checks verified

### Polish (Phase 6)
- **What**: Documentation, testing, logging
- **Why**: Ensures operational reliability and team understanding
- **When**: Final phase
- **Deliverable**: Complete documentation, all tests passing, end-to-end workflow verified

---

## Dependencies & Parallel Execution

### Phase 1-2 Dependencies
Phase 2 MUST complete before Phase 3 begins (foundational setup).

### Phase 3-4 Parallel Execution
US1 (Docker コンテナ化) and US2 (CI/CD パイプライン) tasks can run in parallel after Phase 2:
- T011-T018 (US1 Dockerfiles, compose, env) can run in parallel
- T019-T027 (US2 workflow) can run in parallel  
- Minimal coordination: US1 tasks define Dockerfiles that US2 tasks reference

### Phase 5 Sequential Execution
US3 (本番環境デプロイの簡素化) depends on US1 and US2:
- Cannot start until docker-compose.yml (US1) and workflow (US2) are complete
- Documentation tasks (T028-T034) have no inter-dependencies

### Phase 6 Validation Execution
Polish phase depends on all user stories:
- Testing (T035-T036) can start after US1/US2 setup
- Documentation (T037-T042) runs last

---

## Success Criteria Verification

After all tasks complete:

| 成功基準 | 検証方法 | 対応タスク |
|---------|---------|----------|
| **SC-001**: コンテナ起動 30 秒以内 | `docker compose up -d` + `docker ps` で healthy 確認 | T015, T016, T018 |
| **SC-002**: ワークフロー 5 分以内 | GitHub Actions UI で実行時間確認 | T019-T027, T041 |
| **SC-003**: 全工程自動化 | GitHub Actions 実行ログで test→build→deploy 確認 | T019-T026 |
| **SC-004**: ghcr.io イメージが本番動作 | `docker pull` + `docker compose up` で動作確認 | T026, T041 |
| **SC-005**: main push から 10 分以内 | GitHub Actions UI でエンドツーエンド時間確認 | T041 |

---

## Total Task Count

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 6 tasks  
- **Phase 3 (US1)**: 8 tasks
- **Phase 4 (US2)**: 9 tasks
- **Phase 5 (US3)**: 7 tasks
- **Phase 6 (Polish)**: 8 tasks

**Total**: 42 tasks (4 foundational + 24 story tasks + 8 polish + 6 integration)

**Parallel Opportunities**:
- Phase 2: T005-T009 parallelizable (6 tasks → 1-2 hours)
- Phase 3: T011-T017 parallelizable (7 tasks → 2-3 hours)
- Phase 4: T019-T026 parallelizable (8 tasks → 2-3 hours)
- Phase 5: T028-T033 mostly parallelizable (6 tasks → 1-2 hours)
- Phase 6: Testing + docs parallelizable (8 tasks → 2-3 hours)

**Sequential Bottlenecks**:
- T018 (US1 test) must complete before US2 workflow assumes docker-compose.yml exists
- T027 (US2 test) must complete before T028 (US3 documentation) references workflow behavior
- T041 (E2E test) must run last (depends on all previous phases)

---

## Notes

- All existing pytest tests (49 tests) will run automatically in GitHub Actions workflow
- No new test code required - existing test framework suffices
- All tasks assume rpi-wol/ and pc-power/ directories with existing source code are in place
- Docker and Docker Compose V2+ must be available in development environment
- GitHub Actions is automatically enabled for public repositories
