# NAO Launch Package for HRIStudio Integration

**Enhanced ROS2 launch configurations and utilities for NAO6 robot integration with HRIStudio**

## Overview

The `nao_launch` package provides comprehensive launch files, scripts, and utilities for seamlessly integrating NAO6 robots with the HRIStudio platform. It offers production-ready configurations with safety monitoring, automatic robot management, and optimized performance for human-robot interaction experiments.

## Features

### 🚀 Launch Configurations
- **Production Launch**: Optimized for stable operation with essential features
- **Enhanced Launch**: Full monitoring, safety features, and comprehensive logging
- **Basic Launch**: Simple configuration for development and testing

### 🤖 Robot Management
- **Automatic Wake-up**: Robot automatically awakens on launch
- **Safety Monitoring**: Battery, temperature, and fall detection
- **Emergency Stop**: Immediate motion termination capabilities
- **Status Monitoring**: Real-time robot health and performance tracking

### 🌐 HRIStudio Integration
- **WebSocket Bridge**: Seamless communication via rosbridge
- **Real-time Control**: Direct robot control from web interface
- **Sensor Publishing**: Comprehensive sensor data streaming
- **Performance Optimization**: Tuned frequencies for experiment workflows

### 🛠️ Utilities
- **Control Scripts**: Command-line robot control and monitoring
- **Startup Scripts**: Automated integration setup and launch
- **Diagnostic Tools**: Connectivity testing and troubleshooting

## Quick Start

### 1. Basic Launch
```bash
# Navigate to ROS workspace
cd ~/naoqi_ros2_ws
source install/setup.bash

# Launch with default settings
ros2 launch nao_launch nao6_production.launch.py nao_ip:=nao.local password:=robolab
```

### 2. Using Startup Script
```bash
# Use the comprehensive startup script
cd ~/naoqi_ros2_ws/src/nao_launch/scripts
./start_nao6_hristudio.sh --nao-ip nao.local --password robolab
```

### 3. HRIStudio Connection
```bash
# Start HRIStudio (in another terminal)
cd ~/Documents/Projects/hristudio
bun dev

# Open test interface: http://localhost:3000/nao-test
# Click "Connect" to establish WebSocket connection
```

## Launch Files

### 🔧 `nao6_production.launch.py`
**Recommended for experiments and production use**

Features:
- Optimized sensor frequencies for stability
- Automatic robot wake-up
- Essential safety monitoring
- Robust error handling and recovery
- Performance-tuned for HRIStudio workflows

```bash
ros2 launch nao_launch nao6_production.launch.py \
  nao_ip:=nao.local \
  password:=robolab \
  bridge_port:=9090
```

### 🔍 `nao6_hristudio_enhanced.launch.py`
**For development and comprehensive monitoring**

Features:
- Full safety monitoring and logging
- Advanced error detection and recovery
- Comprehensive sensor publishing
- Debug logging and diagnostics
- Development-friendly configuration

```bash
ros2 launch nao_launch nao6_hristudio_enhanced.launch.py \
  nao_ip:=nao.local \
  password:=robolab \
  enable_safety_monitoring:=true \
  debug_mode:=true
```

### ⚡ `nao6_hristudio.launch.py`
**Simple configuration for basic operation**

Features:
- Minimal configuration
- Fast startup
- Essential robot functionality
- Suitable for testing and development

```bash
ros2 launch nao_launch nao6_hristudio.launch.py \
  nao_ip:=nao.local \
  password:=robolab
```

## Configuration Parameters

### Robot Connection
| Parameter | Default | Description |
|-----------|---------|-------------|
| `nao_ip` | `nao.local` | Robot IP address or hostname |
| `nao_port` | `9559` | NAOqi service port |
| `username` | `nao` | Robot username |
| `password` | `robolab` | Robot password |

### ROS Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `namespace` | `naoqi_driver` | ROS namespace for robot topics |
| `bridge_port` | `9090` | WebSocket bridge port |
| `bridge_address` | `0.0.0.0` | Bridge bind address |

### Publishing Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `publish_joint_states` | `true` | Publish robot joint positions |
| `publish_odometry` | `true` | Publish robot movement data |
| `publish_camera` | `true` | Publish camera feeds |
| `publish_sensors` | `true` | Publish sensor data |

### Safety Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_safety_monitoring` | `true` | Enable safety features |
| `max_linear_velocity` | `0.2` | Maximum linear speed (m/s) |
| `max_angular_velocity` | `0.8` | Maximum rotation speed (rad/s) |
| `auto_wake_up` | `true` | Automatically wake robot |

## Utility Scripts

### 🎮 Robot Control Script
**Direct robot control and monitoring**

```bash
# Basic robot control
python3 scripts/nao_control.py --ip nao.local --password robolab [command]

# Available commands:
python3 scripts/nao_control.py --ip nao.local wake          # Wake up robot
python3 scripts/nao_control.py --ip nao.local speak "Hello" # Make robot speak
python3 scripts/nao_control.py --ip nao.local move 0.1 0 0  # Move forward
python3 scripts/nao_control.py --ip nao.local pose Stand    # Set pose
python3 scripts/nao_control.py --ip nao.local status        # Show status
python3 scripts/nao_control.py --ip nao.local monitor       # Start monitoring
python3 scripts/nao_control.py --ip nao.local emergency     # Emergency stop
```

### 🚀 Startup Script
**Comprehensive integration setup**

```bash
# Full startup with all checks
./scripts/start_nao6_hristudio.sh --nao-ip nao.local --password robolab

# Available options:
--nao-ip IP              # Robot IP address
--password PASS          # Robot password
--bridge-port PORT       # WebSocket port
--production            # Use production config (default)
--enhanced              # Use enhanced config with monitoring
--no-wake               # Skip automatic wake-up
--check-only            # Only perform connectivity checks
--verbose               # Enable debug logging
```

## ROS Topics

### Input Topics (Robot Control)
| Topic | Type | Description |
|-------|------|-------------|
| `/speech` | `std_msgs/String` | Text-to-speech commands |
| `/cmd_vel` | `geometry_msgs/Twist` | Movement commands |
| `/joint_angles` | `naoqi_bridge_msgs/JointAnglesWithSpeed` | Joint control |

### Output Topics (Sensor Data)
| Topic | Type | Description |
|-------|------|-------------|
| `/naoqi_driver/joint_states` | `sensor_msgs/JointState` | Joint positions/velocities |
| `/naoqi_driver/bumper` | `naoqi_bridge_msgs/Bumper` | Foot sensors |
| `/naoqi_driver/hand_touch` | `naoqi_bridge_msgs/HandTouch` | Hand touch sensors |
| `/naoqi_driver/head_touch` | `naoqi_bridge_msgs/HeadTouch` | Head touch sensors |
| `/naoqi_driver/sonar/left` | `sensor_msgs/Range` | Left ultrasonic |
| `/naoqi_driver/sonar/right` | `sensor_msgs/Range` | Right ultrasonic |
| `/naoqi_driver/camera/front/image_raw` | `sensor_msgs/Image` | Front camera |
| `/naoqi_driver/camera/bottom/image_raw` | `sensor_msgs/Image` | Bottom camera |

## WebSocket Integration

### Connection Details
- **URL**: `ws://localhost:9090` (or custom bridge_port)
- **Protocol**: rosbridge v2.0
- **Authentication**: None (local network)

### Message Format
```javascript
// Publish command
{
  "op": "publish",
  "topic": "/speech",
  "type": "std_msgs/String",
  "msg": {"data": "Hello world"}
}

// Subscribe to sensor data
{
  "op": "subscribe",
  "topic": "/naoqi_driver/joint_states",
  "type": "sensor_msgs/JointState"
}
```

## Troubleshooting

### Robot Connection Issues

**Problem**: Cannot connect to robot
```bash
# Test connectivity
ping nao.local
telnet nao.local 9559

# Check SSH access
ssh nao@nao.local
```

**Problem**: Robot not responding to commands
```bash
# Check if robot is awake
python3 scripts/nao_control.py --ip nao.local status

# Wake up robot manually
python3 scripts/nao_control.py --ip nao.local wake
```

### ROS Integration Issues

**Problem**: ROS bridge not working
```bash
# Check if port is available
ss -an | grep 9090

# Kill conflicting processes
sudo fuser -k 9090/tcp

# Restart integration
./scripts/start_nao6_hristudio.sh --nao-ip nao.local
```

**Problem**: Topics not publishing
```bash
# Check ROS topics
ros2 topic list | grep naoqi

# Monitor topic data
ros2 topic echo /naoqi_driver/joint_states --once
```

### HRIStudio Integration Issues

**Problem**: WebSocket connection fails
```bash
# Verify rosbridge is running
ros2 node list | grep rosbridge

# Test WebSocket manually
wscat -c ws://localhost:9090
```

## Safety Guidelines

### ⚠️ Important Safety Notes
- **Always ensure clear space** around the robot during movement
- **Keep emergency stop accessible** - use Ctrl+C or emergency command
- **Monitor battery levels** during long experiments
- **Start with small movements** to verify robot response
- **Never leave robot unattended** during autonomous operation

### Emergency Procedures
```bash
# Immediate stop
python3 scripts/nao_control.py --ip nao.local emergency

# Or via ROS
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'

# Full system shutdown
pkill -f "rosbridge|naoqi|ros2"
```

## Performance Optimization

### Recommended Settings
- **Joint States Frequency**: 20Hz (balance between smoothness and performance)
- **Camera Frequency**: 10Hz (sufficient for monitoring, conserves bandwidth)
- **Sensor Frequency**: 15Hz (responsive touch/bump detection)
- **Maximum Velocity**: 0.2 m/s (safe for indoor experiments)

### Bandwidth Considerations
- **Disable audio publishing** for better performance
- **Reduce camera resolution** if bandwidth is limited
- **Use topic filtering** to publish only required data

## Integration with HRIStudio

### Experiment Design
1. **Install NAO6 plugin** in HRIStudio study
2. **Configure ROS bridge URL**: `ws://localhost:9090`
3. **Design experiments** using available NAO actions
4. **Test robot connectivity** before running trials

### Available Actions
- **Speech synthesis** with customizable text and volume
- **Movement control** with safety limits
- **Pose control** (stand, sit, crouch positions)
- **Head movement** for gaze direction
- **Sensor monitoring** for interaction detection
- **Emergency stop** for safety

## Development

### Building the Package
```bash
# Navigate to workspace
cd ~/naoqi_ros2_ws

# Build package
colcon build --packages-select nao_launch

# Source installation
source install/setup.bash
```

### Testing
```bash
# Run connectivity tests
./scripts/start_nao6_hristudio.sh --check-only

# Test robot control
python3 scripts/nao_control.py --ip nao.local status
```

### Contributing
1. **Follow ROS2 conventions** for launch files and parameters
2. **Test with real NAO6 hardware** before submitting
3. **Update documentation** for any new features
4. **Ensure backward compatibility** with existing configurations

## Version History

### v2.0.0 (Current)
- Enhanced launch configurations with safety monitoring
- Comprehensive utility scripts for robot control
- Production-optimized settings for HRIStudio
- Improved error handling and recovery
- WebSocket integration optimization

### v1.0.0
- Basic NAO6 launch configuration
- Simple rosbridge integration
- Essential robot functionality

## Support

### Requirements
- **ROS2 Humble** (tested and recommended)
- **NAO6 robot** with NAOqi 2.8.7.4
- **Ubuntu 22.04** (or compatible)
- **Network connectivity** to robot

### Documentation
- [HRIStudio Documentation](../docs/)
- [NAO6 Integration Guide](../docs/nao6-integration-complete-guide.md)
- [Quick Reference](../docs/nao6-quick-reference.md)

### Issues and Support
- **GitHub Issues**: [hristudio/nao-integration/issues](https://github.com/hristudio/nao-integration/issues)
- **Email**: robolab@hristudio.com
- **Documentation**: See `docs/` folder for comprehensive guides

---

**License**: MIT  
**Maintainer**: HRIStudio RoboLab Team  
**Version**: 2.0.0  
**Last Updated**: December 2024

*This package is part of the HRIStudio platform for Human-Robot Interaction research.*