#!/usr/bin/env python3
"""
NAO Robot Control and Monitoring Script for HRIStudio Integration

This script provides comprehensive control and monitoring capabilities for NAO6 robots
in HRIStudio experiments. It includes safety features, status monitoring, and
convenient control methods.

Features:
- Robot wake-up/rest control
- Movement and posture commands
- Speech synthesis
- Sensor monitoring
- Emergency stop functionality
- Battery and temperature monitoring
- Connection health checks

Usage:
    python3 nao_control.py --ip nao.local --password robolab [command]

Commands:
    wake        - Wake up the robot
    rest        - Put robot to rest
    status      - Show robot status
    speak TEXT  - Make robot speak
    move X Y Z  - Move robot (x forward, y left, z rotation)
    pose NAME   - Set robot pose (stand, sit, crouch)
    monitor     - Start continuous monitoring
    emergency   - Emergency stop
"""

import argparse
import time
import sys
import json
import threading
import signal
from typing import Dict, List, Optional, Tuple, Any
import subprocess
import socket

# Try to import NAOqi - handle cases where it's not available
try:
    import naoqi
    NAOQI_AVAILABLE = True
except ImportError:
    print("Warning: NAOqi not available. Some features will be disabled.")
    NAOQI_AVAILABLE = False

# Try to import ROS2 libraries
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    from geometry_msgs.msg import Twist
    from sensor_msgs.msg import JointState
    ROS2_AVAILABLE = True
except ImportError:
    print("Warning: ROS2 not available. Using direct NAOqi connection only.")
    ROS2_AVAILABLE = False


class NAOController:
    """Main NAO robot controller class"""

    def __init__(self, robot_ip: str, port: int = 9559, username: str = "nao", password: str = "nao"):
        self.robot_ip = robot_ip
        self.port = port
        self.username = username
        self.password = password

        # NAOqi proxies
        self.motion_proxy = None
        self.tts_proxy = None
        self.audio_proxy = None
        self.memory_proxy = None
        self.battery_proxy = None
        self.system_proxy = None
        self.posture_proxy = None

        # Connection status
        self.connected = False
        self.monitoring = False
        self.monitor_thread = None

        # Safety limits
        self.max_velocity = 0.3  # m/s
        self.max_angular = 1.0   # rad/s

        # Initialize connection
        self.connect()

    def connect(self) -> bool:
        """Establish connection to NAO robot"""
        if not NAOQI_AVAILABLE:
            print("❌ NAOqi not available - cannot connect to robot")
            return False

        try:
            print(f"🔄 Connecting to NAO at {self.robot_ip}:{self.port}...")

            # Test basic connectivity
            if not self._test_connectivity():
                print(f"❌ Cannot reach robot at {self.robot_ip}")
                return False

            # Initialize NAOqi proxies
            self.motion_proxy = naoqi.ALProxy("ALMotion", self.robot_ip, self.port)
            self.tts_proxy = naoqi.ALProxy("ALTextToSpeech", self.robot_ip, self.port)
            self.audio_proxy = naoqi.ALProxy("ALAudioDevice", self.robot_ip, self.port)
            self.memory_proxy = naoqi.ALProxy("ALMemory", self.robot_ip, self.port)
            self.battery_proxy = naoqi.ALProxy("ALBattery", self.robot_ip, self.port)
            self.system_proxy = naoqi.ALProxy("ALSystem", self.robot_ip, self.port)
            self.posture_proxy = naoqi.ALProxy("ALRobotPosture", self.robot_ip, self.port)

            # Test connection with a simple call
            robot_name = self.system_proxy.robotName()
            print(f"✅ Connected to {robot_name}")

            self.connected = True
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            return False

    def _test_connectivity(self) -> bool:
        """Test basic network connectivity to robot"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.robot_ip, self.port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def wake_up(self) -> bool:
        """Wake up the robot"""
        if not self.connected:
            print("❌ Not connected to robot")
            return False

        try:
            print("🌅 Waking up robot...")
            self.motion_proxy.wakeUp()
            time.sleep(2)  # Give robot time to wake up

            # Verify robot is awake
            if self.motion_proxy.robotIsWakeUp():
                print("✅ Robot is awake and ready")
                return True
            else:
                print("⚠️  Robot wake-up may have failed")
                return False

        except Exception as e:
            print(f"❌ Wake-up failed: {e}")
            return False

    def rest(self) -> bool:
        """Put robot to rest position"""
        if not self.connected:
            print("❌ Not connected to robot")
            return False

        try:
            print("😴 Putting robot to rest...")
            self.motion_proxy.rest()
            print("✅ Robot is at rest")
            return True
        except Exception as e:
            print(f"❌ Rest failed: {e}")
            return False

    def speak(self, text: str, volume: float = 0.7) -> bool:
        """Make robot speak"""
        if not self.connected:
            print("❌ Not connected to robot")
            return False

        try:
            print(f"🗣️  Speaking: '{text}'")
            self.tts_proxy.setVolume(volume)
            self.tts_proxy.say(text)
            return True
        except Exception as e:
            print(f"❌ Speech failed: {e}")
            return False

    def move(self, x: float = 0.0, y: float = 0.0, theta: float = 0.0,
             duration: float = 2.0) -> bool:
        """Move robot with velocity commands"""
        if not self.connected:
            print("❌ Not connected to robot")
            return False

        # Apply safety limits
        x = max(min(x, self.max_velocity), -self.max_velocity)
        y = max(min(y, self.max_velocity), -self.max_velocity)
        theta = max(min(theta, self.max_angular), -self.max_angular)

        try:
            print(f"🚶 Moving: x={x:.2f}, y={y:.2f}, θ={theta:.2f} for {duration}s")

            # Enable motion
            if not self.motion_proxy.robotIsWakeUp():
                print("⚠️  Robot not awake - waking up first")
                self.wake_up()

            # Move with velocity
            self.motion_proxy.move(x, y, theta)
            time.sleep(duration)
            self.motion_proxy.stopMove()

            print("✅ Movement completed")
            return True

        except Exception as e:
            print(f"❌ Movement failed: {e}")
            return False

    def set_pose(self, pose_name: str, speed: float = 0.5) -> bool:
        """Set robot to a specific pose"""
        if not self.connected:
            print("❌ Not connected to robot")
            return False

        valid_poses = ["Stand", "Sit", "SitRelax", "StandInit", "StandZero", "Crouch"]

        if pose_name not in valid_poses:
            print(f"❌ Invalid pose. Available: {', '.join(valid_poses)}")
            return False

        try:
            print(f"🤖 Setting pose to: {pose_name}")

            if not self.motion_proxy.robotIsWakeUp():
                self.wake_up()

            self.posture_proxy.goToPosture(pose_name, speed)
            print("✅ Pose set successfully")
            return True

        except Exception as e:
            print(f"❌ Pose setting failed: {e}")
            return False

    def emergency_stop(self) -> bool:
        """Emergency stop - immediately stop all motion"""
        if not self.connected:
            print("❌ Not connected to robot")
            return False

        try:
            print("🛑 EMERGENCY STOP!")
            self.motion_proxy.stopMove()
            self.motion_proxy.killAll()
            print("✅ Emergency stop executed")
            return True
        except Exception as e:
            print(f"❌ Emergency stop failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive robot status"""
        if not self.connected:
            return {"error": "Not connected to robot"}

        status = {}

        try:
            # Basic robot info
            status["robot_name"] = self.system_proxy.robotName()
            status["naoqi_version"] = self.system_proxy.systemVersion()
            status["uptime"] = self.system_proxy.upTime()

            # Motion status
            status["is_awake"] = self.motion_proxy.robotIsWakeUp()
            status["stiffness"] = self.motion_proxy.getStiffnesses("Body")

            # Battery status
            battery_charge = self.battery_proxy.getBatteryCharge()
            status["battery_charge"] = battery_charge
            status["battery_status"] = "Good" if battery_charge > 50 else "Low" if battery_charge > 20 else "Critical"

            # Temperature
            try:
                temp = self.memory_proxy.getData("Device/SubDeviceList/Battery/Temperature/Sensor/Value")
                status["battery_temperature"] = temp
            except:
                status["battery_temperature"] = "Unknown"

            # Joint states (sample)
            try:
                joint_angles = self.motion_proxy.getAngles("Body", True)
                status["joint_count"] = len(joint_angles)
            except:
                status["joint_count"] = "Unknown"

            # Audio status
            try:
                volume = self.tts_proxy.getVolume()
                status["audio_volume"] = volume
            except:
                status["audio_volume"] = "Unknown"

        except Exception as e:
            status["error"] = str(e)

        return status

    def start_monitoring(self, interval: float = 5.0):
        """Start continuous robot monitoring"""
        if self.monitoring:
            print("⚠️  Monitoring already active")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print(f"📊 Started monitoring (interval: {interval}s)")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            print("🛑 Monitoring stopped")

    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                status = self.get_status()

                # Print essential status
                if "error" not in status:
                    battery = status.get("battery_charge", 0)
                    awake = status.get("is_awake", False)
                    temp = status.get("battery_temperature", "?")

                    status_emoji = "🟢" if awake else "🔴"
                    battery_emoji = "🔋" if battery > 50 else "🪫" if battery > 20 else "⚡"

                    print(f"{status_emoji} Robot: {'Awake' if awake else 'Sleeping'} | "
                          f"{battery_emoji} Battery: {battery}% | "
                          f"🌡️  Temp: {temp}°C")
                else:
                    print(f"❌ Monitoring error: {status['error']}")

            except Exception as e:
                print(f"❌ Monitor loop error: {e}")

            time.sleep(interval)

    def close(self):
        """Clean up connections"""
        self.stop_monitoring()
        self.connected = False
        print("🔌 Disconnected from robot")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="NAO Robot Control Script")
    parser.add_argument("--ip", default="nao.local", help="Robot IP address")
    parser.add_argument("--port", type=int, default=9559, help="NAOqi port")
    parser.add_argument("--username", default="nao", help="Robot username")
    parser.add_argument("--password", default="robolab", help="Robot password")
    parser.add_argument("--max-velocity", type=float, default=0.3, help="Max velocity (m/s)")

    # Commands
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()

    # Create controller
    controller = NAOController(args.ip, args.port, args.username, args.password)
    controller.max_velocity = args.max_velocity

    if not controller.connected:
        print("❌ Failed to connect to robot")
        return 1

    # Handle CTRL+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Interrupted - cleaning up...")
        controller.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Execute command
    command = args.command.lower()
    cmd_args = args.args

    try:
        if command == "wake":
            success = controller.wake_up()

        elif command == "rest":
            success = controller.rest()

        elif command == "speak":
            if not cmd_args:
                print("❌ Usage: speak TEXT")
                return 1
            text = " ".join(cmd_args)
            success = controller.speak(text)

        elif command == "move":
            if len(cmd_args) != 3:
                print("❌ Usage: move X Y THETA")
                return 1
            try:
                x, y, theta = map(float, cmd_args)
                success = controller.move(x, y, theta)
            except ValueError:
                print("❌ Invalid movement values")
                return 1

        elif command == "pose":
            if not cmd_args:
                print("❌ Usage: pose POSE_NAME")
                return 1
            pose_name = cmd_args[0]
            success = controller.set_pose(pose_name)

        elif command == "status":
            status = controller.get_status()
            print("\n📊 Robot Status:")
            print(json.dumps(status, indent=2))
            success = True

        elif command == "monitor":
            print("📊 Starting continuous monitoring (Ctrl+C to stop)...")
            controller.start_monitoring()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            success = True

        elif command == "emergency":
            success = controller.emergency_stop()

        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: wake, rest, speak, move, pose, status, monitor, emergency")
            success = False

        controller.close()
        return 0 if success else 1

    except Exception as e:
        print(f"❌ Command execution failed: {e}")
        controller.close()
        return 1


if __name__ == "__main__":
    exit(main())
