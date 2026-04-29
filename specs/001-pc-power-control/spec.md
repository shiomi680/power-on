# Feature Specification: Remote PC Power Control

**Feature Branch**: `001-pc-power-control`  
**Created**: 2026-04-29  
**Status**: Draft  
**Input**: User description: "Remote power control for PC from Android device using Raspberry Pi with Wake-on-LAN and Flask APIs"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Android User Powers On PC (Priority: P1)

An Android user wants to remotely turn on their PC when they're away from home. They send a power-on command from their Android device, which reaches the Raspberry Pi. The Raspberry Pi then broadcasts a Wake-on-LAN (WOL) magic packet to the PC, causing it to wake from sleep or powered-off state.

**Why this priority**: Core functionality that enables the primary use case - remote power-on capability is the most valuable feature.

**Independent Test**: Can be fully tested by sending a power-on request from Android, receiving confirmation that WOL packet was sent, and verifying PC wakes up.

**Acceptance Scenarios**:

1. **Given** Android device has network access and Raspberry Pi is running, **When** user taps power-on button on Android, **Then** Raspberry Pi receives the request and sends WOL packet to PC within 2 seconds
2. **Given** PC is powered off or in sleep mode, **When** WOL packet is sent, **Then** PC turns on and boots successfully
3. **Given** PC is already powered on, **When** power-on request is sent, **Then** system acknowledges request gracefully (does not cause errors)

---

### User Story 2 - Android User Powers Off PC (Priority: P1)

An Android user wants to remotely shut down their PC. They send a power-off command from their Android device, which reaches the PC directly. The PC receives the command and initiates a graceful shutdown.

**Why this priority**: Core functionality - power-off is equally important as power-on for complete control.

**Independent Test**: Can be fully tested by sending a shutdown request from Android, verifying PC receives it, and confirming PC shuts down within reasonable time.

**Acceptance Scenarios**:

1. **Given** PC is powered on and Flask server is running, **When** user taps power-off button on Android, **Then** PC receives shutdown command and initiates shutdown within 5 seconds
2. **Given** PC is shutting down, **When** users send another command, **Then** system gracefully handles the request (either acknowledges ongoing shutdown or queues command)

---

### User Story 3 - Android User Checks PC Status (Priority: P2)

An Android user wants to know whether their PC is currently powered on or off before deciding to send commands. They can request the current power status from the PC.

**Why this priority**: High value - users want to verify the current state before sending commands, improves user experience and prevents confusion about command results.

**Independent Test**: Can be fully tested by querying PC status and verifying the response accurately reflects whether PC is powered on or off.

**Acceptance Scenarios**:

1. **Given** PC is powered on with Flask server running, **When** Android sends status query, **Then** PC responds with "online" status within 2 seconds
2. **Given** PC is powered off, **When** Android sends status query, **Then** Raspberry Pi responds with "offline" status (PC cannot respond directly)
3. **Given** PC is powered on but Flask server is not running, **When** Android sends status query, **Then** system responds with appropriate error or "unreachable" status

---

### Edge Cases

- What happens if network connection drops between Android and Raspberry Pi?
- How does the system handle when PC's WOL magic packet recipient is disabled in BIOS?
- What happens if multiple power commands are sent in rapid succession?
- How does system behave when Raspberry Pi loses network connectivity?
- What if PC is in the middle of shutdown when another power-on command arrives?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow Android device to send power-on command to Raspberry Pi
- **FR-002**: Raspberry Pi MUST receive power-on commands from Android and broadcast WOL magic packet to target PC MAC address
- **FR-003**: System MUST allow Android device to send power-off command directly to PC
- **FR-004**: PC MUST receive shutdown commands and initiate graceful system shutdown
- **FR-005**: System MUST allow Android device to query the power status of PC
- **FR-006**: Raspberry Pi MUST respond with PC status when queried by Android (either "online" or "offline")
- **FR-007**: PC MUST respond with its status (online/available) when directly queried by Android
- **FR-008**: Raspberry Pi MUST expose HTTP endpoint for receiving power-on requests from Android
- **FR-009**: PC MUST expose HTTP endpoint for receiving shutdown requests from Android
- **FR-010**: PC MUST expose HTTP endpoint for responding to status queries from Android
- **FR-011**: System MUST handle cases where commands arrive when PC is already in target state (e.g., power-on when already on)

### Key Entities

- **Android Client**: Mobile device sending control commands
- **Raspberry Pi**: Intermediary device hosting power-on service, broadcasts WOL packets
- **PC**: Target device receiving shutdown commands and status queries
- **WOL Magic Packet**: Network packet containing PC's MAC address that wakes PC from sleep
- **HTTP Endpoint**: Network interface for receiving and responding to commands
- **PC Power State**: Current state tracked as "online" (powered on) or "offline" (powered off)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Android user can turn PC on within 3 seconds of tapping power-on button (response time from Android to Raspberry Pi)
- **SC-002**: PC completes shutdown within 30 seconds of receiving power-off command
- **SC-003**: System accurately reports PC power status 95% of the time when queried
- **SC-004**: All three operations (power-on, power-off, status check) are independently functional and testable

## Assumptions

- Android device and Raspberry Pi are on the same network (or can communicate via network)
- PC and Raspberry Pi are on the same network for WOL packet delivery
- PC has WOL capability enabled in BIOS/firmware
- PC's MAC address is known and configured in the Raspberry Pi
- Users have basic network connectivity (WiFi or Ethernet)
- Initial setup and configuration of network details (IP addresses, MAC addresses) is a separate process from this feature
- Graceful shutdown is preferred over hard power-off
- HTTP communication is acceptable for LAN environment (security hardening is out of scope for v1)
