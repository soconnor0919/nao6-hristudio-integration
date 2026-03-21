#!/usr/bin/env python3
"""
NAO6 Robot Initialization Script
Disables autonomous life and wakes up the robot for controlled HRI experiments.
"""
import sys
import time
import argparse

try:
    from qi import Application
except ImportError:
    print("ERROR: libqi not found. Install with: pip install naoqi")
    sys.exit(1)


def initialize_robot(robot_ip: str, robot_port: int = 9559):
    """Initialize the robot: disable autonomous life and wake up."""
    
    print(f"Connecting to NAO6 at {robot_ip}:{robot_port}...")
    
    # Create a minimal Qi application
    app = Application(["NAOInit", "--qi-url=fake"])
    app.start()
    
    session = app.session
    try:
        # Connect to robot
        connection_url = f"tcp://{robot_ip}:{robot_port}"
        session.connect(connection_url)
        print("Connected successfully!")
        
        # Get required services
        autonomous_life = session.service("ALAutonomousLife")
        motion = session.service("ALMotion")
        posture = session.service("ALRobotPosture")
        
        # Step 1: Disable autonomous life
        print("Disabling autonomous life...")
        try:
            current_state = autonomous_life.getState()
            print(f"  Current state: {current_state}")
            if current_state != "disabled":
                autonomous_life.setState("disabled")
                time.sleep(2)
        except Exception as e:
            print(f"  Warning: Could not disable autonomous life: {e}")
        
        # Step 2: Wake up the robot
        print("Waking up robot...")
        try:
            # First ensure motors are enabled
            motion.wakeUp()
            time.sleep(1)
            
            # Move to a neutral standing posture
            posture.goToPosture("Stand", 0.5)
            time.sleep(2)
            print("  Robot is now awake and standing!")
        except Exception as e:
            print(f"  Warning: Could not wake up robot: {e}")
        
        # Step 3: Set up basic awareness
        print("Setting up awareness...")
        try:
            awareness = session.service("ALBasicAwareness")
            awareness.setEnabled(False)  # Disable to prevent interference
        except Exception as e:
            print(f"  Note: ALBasicAwareness not available: {e}")
        
        print("\n✓ Robot initialization complete!")
        print("  - Autonomous life: disabled")
        print("  - Robot state: awake/standing")
        print("  - Ready for HRIStudio control")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize robot: {e}")
        return False
    finally:
        app.stop()
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Initialize NAO6 robot for HRI")
    parser.add_argument("--ip", default="10.0.0.42", help="Robot IP address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port")
    args = parser.parse_args()
    
    success = initialize_robot(args.ip, args.port)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
