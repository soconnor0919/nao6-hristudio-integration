# NAO6 HRIStudio Integration

Docker image for NAO6 robot control with HRIStudio.

## Setup

```bash
git clone --recursive <repo> nao6-hristudio-integration
cd nao6-hristudio-integration
docker compose build
```

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
