# NAO6 HRIStudio Integration

Docker image for NAO6 robot control with HRIStudio.

## Quick Start

```bash
git clone --recurse-submodules https://github.com/soconnor0919/nao6-hristudio-integration.git
cd nao6-hristudio-integration
docker compose build
NAO_IP=192.168.1.100 docker compose up -d
```

## Setup

### Prerequisites
- Docker and Docker Compose v2
- NAO6 robot on same network

### Clone with Submodules

```bash
git clone --recurse-submodules https://github.com/soconnor0919/nao6-hristudio-integration.git
cd nao6-hristudio-integration
docker compose build
```

**Note:** If you cloned without `--recurse-submodules`, the ROS packages will still be downloaded automatically on first build.

## Run

```bash
NAO_IP=192.168.1.100 docker compose up -d
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NAO_IP` | `nao.local` | Robot IP address |
| `NAO_PASSWORD` | `robolab` | Robot SSH password |
| `NAO_USERNAME` | `nao` | Robot SSH username |
| `BRIDGE_PORT` | `9090` | WebSocket port |

## Services

- **nao_driver** - Connects to robot
- **ros_bridge** - WebSocket (ws://localhost:9090)
- **ros_api** - Topic/service introspection

## Stop

```bash
docker compose down
```

## Troubleshooting

### mDNS hostname not resolving
If `nao.local` doesn't work, specify the IP directly:
```bash
NAO_IP=192.168.1.100 docker compose up
```

### Find your robot's IP
On the robot, say "What is my IP address?" or check the robot's network settings.
