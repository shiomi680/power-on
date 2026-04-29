# Power-On: Remote PC Power Control System

[![GitHub Actions: CI/CD](https://github.com/shiomi680/power-on/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/shiomi680/power-on/actions)
[![Container Registry](https://img.shields.io/badge/registry-ghcr.io-blue)](https://github.com/shiomi680/power-on/pkgs/container/)

Remote wake-on-LAN (WOL) and power management system for controlling PC power state from a Raspberry Pi. Deploy using Docker for easy multi-platform support.

## Table of Contents

- [Quick Start (5 minutes)](#quick-start)
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Deployment Guides](#deployment-guides)
  - [Raspberry Pi WOL Service](#raspberry-pi-wol-service)
  - [PC Power Control API](#pc-power-control-api)
  - [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Related Documentation](#related-documentation)

---

## Quick Start

Deploy both services with a single Docker Compose command:

```bash
# Clone the repository
git clone https://github.com/shiomi680/power-on.git
cd power-on

# Copy environment template and configure (see Environment Variables section)
# For basic testing, you can use default values in docker-compose.yml

# Start both services
docker compose up -d

# Verify services are running
curl http://localhost:5000/health     # Raspberry Pi WOL service
curl http://localhost:5001/health     # PC power control API
```

**Expected output**:
- Raspberry Pi Web UI: http://localhost:5000 (working)
- PC API health check: returns `{"status": "ok"}` (port 5001)

Both services should be running within 2 minutes.

---

## Prerequisites

### System Requirements

| Component | Requirement | Notes |
|-----------|------------|-------|
| **CPU** | 64-bit processor | Raspberry Pi 3B+ or newer recommended |
| **RAM** | 2GB minimum | 4GB+ recommended for comfort |
| **Storage** | 4GB available | After OS and Docker installation |
| **Network** | Ethernet or WiFi | Must be on same LAN as target PC |

### Software Requirements

| Software | Version | Installation |
|----------|---------|--------------|
| **Docker** | v20.10 or later | [Docker Installation Guide](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2.0 or later (V2 only) | Included with Docker Desktop |
| **Git** | Any recent version | `sudo apt install git` (Linux/RPi) |
| **Python** | 3.10 or later (native deployment only) | Pre-installed on most systems |

### Network Requirements

| Item | Requirement | Notes |
|------|------------|-------|
| **WOL Port** | UDP 5000 or custom | Typically broadcast address |
| **Firewall** | Allow UDP broadcast | For WOL magic packets |
| **PC Port** | TCP 5001 or custom | For power control API communication |
| **Subnet** | Same LAN as target PC | WOL requires same broadcast domain |

### Hardware-Specific Notes

**For Raspberry Pi**:
- Ethernet connection strongly recommended over WiFi
- May need to adjust `docker-compose.yml` for low-memory systems (Pi Zero/Zero2)
- Systemd service can be configured for auto-start on boot

**For Windows PC**:
- Ensure "Wake-On-LAN" enabled in BIOS
- Windows Defender may need port exception for power control API
- If running on Windows Server, ensure "Network Interface" hardware access is enabled

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         User / Administrator                │
│                                             │
│  Web Browser          System CLI            │
│  (http://rpi:5000)    (docker, ssh, etc.)  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   Raspberry Pi  │
        │   WOL Service   │
        │  (Port 5000)    │
        │                 │
        │ - Flask Web UI  │
        │ - REST API      │
        │ - WOL packets   │
        └────────┬────────┘
                 │
        ┌────────┴──────────┐
        │ Broadcast Network │
        │ (UDP multicast)   │
        │ (IP: 255.255...)  │
        └────────┬──────────┘
                 │
                 ▼
        ┌─────────────────┐
        │    PC System    │
        │                 │
        │ Power Control   │
        │ API (5001)      │
        │                 │
        │ - Status check  │
        │ - Shutdown cmd  │
        │ - Power state   │
        └─────────────────┘
```

**Components**:
- **Raspberry Pi WOL Service**: Runs on Raspberry Pi, exposes Flask Web UI and REST API for power control
- **PC Power API**: Runs on target PC, controls system power state and provides health checks
- **Docker Registry**: Images stored at `ghcr.io/shiomi680/power-on-rpi` and `ghcr.io/shiomi680/power-on-pc`

**Communication Flow**:
1. User sends command via Web UI or API (Raspberry Pi, port 5000)
2. Raspberry Pi generates WOL magic packet or HTTP API call
3. PC wakes up from sleep or executes power command
4. Status returned to user via Web UI or API response

---

## Deployment Guides

### Raspberry Pi WOL Service

**Time estimate**: 10-15 minutes  
**Difficulty**: Beginner  
**Target**: Raspberry Pi 3B+ or newer (4GB RAM recommended)

#### Step 1: Clone Repository

```bash
# SSH into Raspberry Pi
ssh pi@<rpi-ip-address>

# Clone the repository
git clone https://github.com/shiomi680/power-on.git
cd power-on
```

**Expected output**:
```
Cloning into 'power-on'...
remote: Enumerating objects...
[progress messages]
done.
```

#### Step 2: Configure Environment Variables

Edit `.env` file with your PC's details:

```bash
# Copy environment template
cp rpi-wol/.env.example rpi-wol/.env

# Edit with your PC information
nano rpi-wol/.env
```

**Configure these values**:

| Variable | Example | Description |
|----------|---------|-------------|
| `PC_ADDRESS` | `192.168.1.100` | Your PC's IP address on the network |
| `PC_API_PORT` | `5001` | Port where PC API listens |
| `PC_API_TIMEOUT` | `5` | Timeout for PC API calls (seconds) |
| `WOL_TARGET_MAC` | `aa:bb:cc:dd:ee:ff` | Your PC's MAC address |
| `WOL_BROADCAST_IP` | `255.255.255.255` | Broadcast address (usually `255.255.255.255`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |

**How to find your PC's MAC address**:

- **Linux**: `ip addr show` (look for `link/ether` entry)
- **macOS**: `ifconfig` (look for `ether` entry)
- **Windows**: `ipconfig /all` (look for `Physical Address`)

#### Step 3: Start the Service

```bash
# Start Raspberry Pi WOL service
cd power-on/rpi-wol
docker compose up -d
```

**Expected output**:
```
[+] Running 2/2
 ✔ Container power-on-rpi-web-1      Started
 ✔ Container power-on-rpi-redis-1     Started
```

#### Step 4: Verify Service is Running

```bash
# Check container status
docker compose ps

# Test health endpoint
curl http://localhost:5000/health
```

**Expected health check response**:
```json
{
  "status": "ok",
  "service": "rpi-wol",
  "timestamp": "2026-04-29T10:00:00Z"
}
```

#### Step 5: Access Web UI

Open in browser: `http://<rpi-ip-address>:5000`

You should see the Power Control dashboard with buttons to control the PC power state.

---

### PC Power Control API

**Time estimate**: 5-10 minutes  
**Difficulty**: Beginner  
**Target**: Windows, Linux, or macOS PC

#### Step 1: Clone Repository

```bash
# On the PC you want to control
git clone https://github.com/shiomi680/power-on.git
cd power-on
```

#### Step 2: Configure Environment Variables

```bash
# Copy environment template
cp pc-power/.env.example pc-power/.env

# Edit configuration (adjust SHUTDOWN_TIMEOUT if needed)
# nano pc-power/.env    (Linux/macOS)
# notepad pc-power\.env (Windows PowerShell)
```

**Configure these values**:

| Variable | Default | Description |
|----------|---------|-------------|
| `SHUTDOWN_TIMEOUT` | `60` | Seconds to wait before shutdown (allows save/cleanup) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |

#### Step 3: Start the Service

```bash
# Linux/macOS
cd power-on/pc-power
docker compose up -d

# Or manually with Python
cd power-on/pc-power
pip install -r requirements.txt
python -m src.flask_app
```

**Expected output**:
```
[+] Running 1/1
 ✔ Container power-on-pc-api-1       Started
```

#### Step 4: Verify API is Running

```bash
# Check health endpoint
curl http://localhost:5001/health
```

**Expected response**:
```json
{
  "status": "ok",
  "service": "pc-power",
  "timestamp": "2026-04-29T10:00:00Z"
}
```

#### Step 5: Test Power Control API

```bash
# Get current power state
curl http://localhost:5001/api/power/status

# Example response
{"state": "on", "uptime_seconds": 3600}
```

---

### Docker Deployment (Both Services)

**Time estimate**: 2-3 minutes  
**Difficulty**: Beginner  
**Recommended**: Use this method for simplest deployment

#### Quick Start with Docker Compose

From repository root:

```bash
# Copy environment templates
cp rpi-wol/.env.example rpi-wol/.env
cp pc-power/.env.example pc-power/.env

# Edit files to configure PC_ADDRESS and MAC address
nano rpi-wol/.env

# Start both services
docker compose up -d
```

#### Verify Both Services

```bash
# List running containers
docker compose ps

# Test Raspberry Pi service (WOL)
curl http://localhost:5000/health

# Test PC service (Power API)
curl http://localhost:5001/health
```

**Expected output**:
```
NAME                     COMMAND                  SERVICE      STATUS
power-on-rpi-web        python -m src.flask_app  rpi-wol      Up 2 minutes
power-on-rpi-redis      redis-server             rpi-wol      Up 2 minutes
power-on-pc-api         python -m src.flask_app  pc-power     Up 2 minutes
```

#### Pull Pre-Built Images

If you have GitHub Container Registry access:

```bash
# Pull images from ghcr.io
docker pull ghcr.io/shiomi680/power-on-rpi:latest
docker pull ghcr.io/shiomi680/power-on-pc:latest

# Reference in docker-compose.yml:
# image: ghcr.io/shiomi680/power-on-rpi:latest
```

---

## Environment Variables

Complete reference for all configuration options.

### Raspberry Pi WOL Service (`rpi-wol/.env`)

| Variable | Required | Default | Example | Description |
|----------|----------|---------|---------|-------------|
| `PC_ADDRESS` | ✅ Yes | - | `192.168.1.100` | Target PC IP address or hostname |
| `PC_API_PORT` | ✅ Yes | - | `5001` | Port where PC API listens |
| `PC_API_TIMEOUT` | ❌ No | `5` | `10` | API timeout in seconds |
| `WOL_TARGET_MAC` | ✅ Yes | - | `aa:bb:cc:dd:ee:ff` | Target PC MAC address |
| `WOL_BROADCAST_IP` | ❌ No | `255.255.255.255` | `192.168.1.255` | Broadcast address for WOL packets |
| `FLASK_HOST` | ❌ No | `0.0.0.0` | `localhost` | Flask server bind address |
| `FLASK_PORT` | ❌ No | `5000` | `5000` | Flask server port |
| `LOG_LEVEL` | ❌ No | `INFO` | `DEBUG` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### PC Power Control API (`pc-power/.env`)

| Variable | Required | Default | Example | Description |
|----------|----------|---------|---------|-------------|
| `SHUTDOWN_TIMEOUT` | ❌ No | `60` | `120` | Seconds before shutdown (allows cleanup) |
| `FLASK_HOST` | ❌ No | `0.0.0.0` | `localhost` | Flask server bind address |
| `FLASK_PORT` | ❌ No | `5001` | `5001` | Flask server port |
| `LOG_LEVEL` | ❌ No | `INFO` | `DEBUG` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Template Files

Start with provided templates:

```bash
# Raspberry Pi template
cat rpi-wol/.env.example

# PC template
cat pc-power/.env.example
```

---

## Troubleshooting

### Common Issues & Solutions

#### Port 5000 or 5001 Already in Use

**Symptom**: `Address already in use` or `bind: permission denied`

**Solution**:
```bash
# Find process using the port (Linux/macOS)
lsof -i :5000
lsof -i :5001

# Kill the process (replace PID)
kill -9 <PID>

# Or change port in docker-compose.yml
# Edit: ports: - "8000:5000"  (use port 8000 instead)
```

#### Cannot Connect to PC from Raspberry Pi

**Symptom**: Web UI works, but power control commands fail

**Diagnosis**:
```bash
# Test network connectivity to PC
ping <PC_ADDRESS>

# Test API directly
curl http://<PC_ADDRESS>:5001/health

# Check firewall on PC
# - Windows: Allow port 5001 in Windows Defender
# - Linux: Check iptables/ufw rules
```

**Solution**:
- Verify `PC_ADDRESS` in `.env` is correct (use IP, not hostname, initially)
- Ensure both devices on same LAN/subnet
- Check firewall settings on PC
- Verify PC power API is running: `curl http://localhost:5001/health`

#### Docker Container Exits Immediately

**Symptom**: `docker compose ps` shows "Exited"

**Diagnosis**:
```bash
# Check container logs
docker compose logs rpi-wol

# Or specific container
docker logs power-on-rpi-web-1
```

**Solution**:
- Check for Python import errors in logs
- Ensure `.env` file exists and is readable
- Verify all required environment variables set
- Check Docker daemon is running: `docker ps`

#### WOL Magic Packet Not Received

**Symptom**: PC doesn't wake up when WOL command sent

**Diagnosis**:
```bash
# Check MAC address is correct
ip addr show         # (on PC)

# Test WOL locally (on Raspberry Pi)
arp-scan -l          # Verify PC MAC on network
```

**Solution**:
- Verify MAC address in `.env` (use `ip addr` or `ipconfig /all`)
- Check BIOS: Wake-On-LAN must be enabled on PC
- Ensure Raspberry Pi can reach broadcast address: `ping 255.255.255.255`
- Try narrowed broadcast: Set `WOL_BROADCAST_IP` to subnet broadcast (e.g., `192.168.1.255`)

#### Permission Denied Errors

**Symptom**: `Permission denied` or `Operation not permitted`

**Solution** (Linux/Raspberry Pi):
```bash
# Ensure current user can access Docker
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker compose up -d
```

#### High CPU Usage or Memory Issues

**Symptom**: System becomes slow, processes killed

**Solution**:
```bash
# Check resource usage
docker stats

# For low-memory systems (Pi Zero), edit docker-compose.yml:
# Add: deploy:
#        resources:
#          limits:
#            memory: 256M
```

#### Connection Timeout or Network Issues

**Symptom**: `Connection refused`, `Network is unreachable`, or timeouts

**Diagnosis**:
```bash
# From Raspberry Pi, test PC connectivity
nc -zv <PC_ADDRESS> 5001    # netcat test
curl -v http://<PC_ADDRESS>:5001/health

# Check network routing
ip route
```

**Solution**:
- Verify both devices on same subnet (use `ping` from both directions)
- Check router/network configuration
- Increase `PC_API_TIMEOUT` in `.env` for slow networks
- Ensure no network ACLs blocking traffic

#### Redis Connection Issues

**Symptom**: Redis service fails to start (Docker logs show error)

**Solution**:
```bash
# Redis is used by rpi-wol for caching
# Ensure Docker has sufficient disk space
docker system df

# Clear unused images if needed
docker system prune
```

### Getting Help

1. Check logs first:
   ```bash
   docker compose logs --tail 50
   ```

2. Verify all .env variables:
   ```bash
   cat rpi-wol/.env
   ```

3. Test endpoints manually:
   ```bash
   curl http://localhost:5000/health
   curl http://localhost:5001/health
   ```

4. Check network configuration:
   ```bash
   ifconfig              # (Linux/macOS)
   ipconfig              # (Windows)
   ping <target-ip>
   arp-scan -l           # (Linux/macOS)
   ```

---

## Related Documentation

For more detailed information, see:

- **[Docker Deployment](docs/DOCKER.md)** - Docker images, registry, health checks
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment on hardware
- **[CI/CD Pipeline](docs/CI-CD.md)** - GitHub Actions, automated testing, image building
- **[Architecture](docs/ARCHITECTURE.md)** - System design and component details

---

## Development

### Prerequisites for Development

```bash
# Clone repository
git clone https://github.com/shiomi680/power-on.git
cd power-on

# Create virtual environment
python -m venv venv
source venv/bin/activate  # (Linux/macOS)
# or
py -m venv venv && venv\Scripts\activate  # (Windows)

# Install dependencies
pip install -r rpi-wol/requirements.txt
pip install -r pc-power/requirements.txt

# Run tests
pytest rpi-wol/tests/
pytest pc-power/tests/
```

### Running Locally (without Docker)

```bash
# Terminal 1: Raspberry Pi WOL service
cd rpi-wol
export FLASK_PORT=5000
python -m src.flask_app

# Terminal 2: PC Power API
cd pc-power
export FLASK_PORT=5001
python -m src.flask_app
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

All contributions should include tests and documentation.

---

## License

MIT License - see LICENSE file for details

---

**Last Updated**: 2026-04-29  
**Maintained by**: Genki Team  
**Issues**: [GitHub Issues](https://github.com/shiomi680/power-on/issues)
