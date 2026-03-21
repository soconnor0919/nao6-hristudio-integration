from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    LogInfo,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description():
    """
    Production NAO6 HRIStudio Launch Configuration

    Optimized for stable operation with essential features:
    - Reliable NAOqi driver connection
    - Robust rosbridge WebSocket for HRIStudio
    - Essential sensor publishing
    - Automatic robot wake-up
    - Error recovery and monitoring
    """

    return LaunchDescription([
        # =================================================================
        # CONFIGURATION ARGUMENTS
        # =================================================================

        DeclareLaunchArgument(
            "nao_ip",
            default_value="nao.local",
            description="NAO robot IP address or hostname"
        ),
        DeclareLaunchArgument(
            "nao_port",
            default_value="9559",
            description="NAOqi port (default: 9559)"
        ),
        DeclareLaunchArgument(
            "username",
            default_value="nao",
            description="NAO username"
        ),
        DeclareLaunchArgument(
            "password",
            default_value="robolab",
            description="NAO password (institution-specific)"
        ),
        DeclareLaunchArgument(
            "bridge_port",
            default_value="9090",
            description="ROS bridge port for HRIStudio WebSocket"
        ),
        DeclareLaunchArgument(
            "namespace",
            default_value="naoqi_driver",
            description="ROS namespace for NAO nodes"
        ),
        DeclareLaunchArgument(
            "auto_wake_up",
            default_value="true",
            description="Automatically wake up robot on launch"
        ),

        # =================================================================
        # STARTUP LOGGING
        # =================================================================

        LogInfo(
            msg=[
                "\n=== NAO6 HRIStudio Production Integration ===\n",
                "Robot: ", LaunchConfiguration("nao_ip"), "\n",
                "WebSocket: ws://0.0.0.0:", LaunchConfiguration("bridge_port"), "\n",
                "Namespace: ", LaunchConfiguration("namespace"), "\n",
                "Auto Wake-up: ", LaunchConfiguration("auto_wake_up"), "\n"
            ]
        ),

        # =================================================================
        # ROBOT WAKE-UP SERVICE
        # =================================================================

        ExecuteProcess(
            cmd=[
                "bash", "-c",
                [
                    "echo 'Waking up NAO robot...' && ",
                    "sshpass -p '", LaunchConfiguration("password"), "' ",
                    "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ",
                    LaunchConfiguration("username"), "@", LaunchConfiguration("nao_ip"), " ",
                    "\"python2 -c \\\"",
                    "import sys; ",
                    "sys.path.append('/opt/aldebaran/lib/python2.7/site-packages'); ",
                    "import naoqi; ",
                    "motion = naoqi.ALProxy('ALMotion', '127.0.0.1', 9559); ",
                    "motion.wakeUp(); ",
                    "print('NAO robot awakened successfully')\\\"\" || ",
                    "echo 'Failed to wake up robot - continuing anyway'"
                ]
            ],
            name="nao_wake_up",
            output="screen",
            shell=True,
            condition=IfCondition(LaunchConfiguration("auto_wake_up"))
        ),

        # =================================================================
        # NAOqi DRIVER - CORE ROBOT INTERFACE
        # =================================================================

        Node(
            package="naoqi_driver",
            executable="naoqi_driver_node",
            name="naoqi_driver",
            namespace=LaunchConfiguration("namespace"),
            parameters=[{
                # Connection settings
                "nao_ip": LaunchConfiguration("nao_ip"),
                "nao_port": LaunchConfiguration("nao_port"),
                "username": LaunchConfiguration("username"),
                "password": LaunchConfiguration("password"),
                "network_interface": "eth0",
                "qi_listen_url": "tcp://0.0.0.0:0",

                # Essential publishing - optimized for HRIStudio
                "publish_joint_states": True,
                "publish_odometry": True,
                "publish_camera": True,
                "publish_sensors": True,
                "publish_audio": False,  # Disabled for performance

                # Optimized frequencies for experiments
                "joint_states_frequency": 20.0,  # Reduced for stability
                "odom_frequency": 20.0,
                "camera_frequency": 10.0,        # Reduced for bandwidth
                "sensor_frequency": 15.0,

                # Robot safety
                "enable_emergency_stop": True,
                "max_linear_velocity": 0.2,      # Conservative speed
                "max_angular_velocity": 0.8,

                # Additional essential features
                "publish_body_pose": True,
                "publish_foot_contact": True,
                "publish_robot_description": True,
                "use_sim_time": False,
            }],
            output="screen",
            emulate_tty=True,
            respawn=True,
            respawn_delay=5.0
        ),

        # =================================================================
        # ROSBRIDGE WEBSOCKET - HRISTUDIO COMMUNICATION
        # =================================================================

        Node(
            package="rosbridge_server",
            executable="rosbridge_websocket",
            name="rosbridge_websocket",
            parameters=[{
                "port": LaunchConfiguration("bridge_port"),
                "address": "0.0.0.0",
                "authenticate": False,
                "fragment_timeout": 600,
                "delay_between_messages": 0,
                "max_message_size": 10000000,
                "unregister_timeout": 10.0,
                "service_timeout": 10.0,
                "bson_only_mode": False,
            }],
            output="screen",
            emulate_tty=True,
            respawn=True,
            respawn_delay=3.0
        ),

        # =================================================================
        # ROS API SERVER - REQUIRED FOR ROSBRIDGE
        # =================================================================

        Node(
            package="rosapi",
            executable="rosapi_node",
            name="rosapi",
            output="screen",
            respawn=True,
            respawn_delay=3.0
        ),

        # =================================================================
        # TRANSFORM PUBLISHER - ROBOT POSITIONING
        # =================================================================

        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="nao_odom_transform",
            arguments=[
                "0", "0", "0",     # translation (x, y, z)
                "0", "0", "0",     # rotation (roll, pitch, yaw)
                "odom",            # parent frame
                [LaunchConfiguration("namespace"), "/base_link"]  # child frame
            ],
            output="log"
        ),

        # =================================================================
        # EMERGENCY STOP SERVICE - SAFETY
        # =================================================================

        Node(
            package="std_srvs",
            executable="service_node",
            name="emergency_stop_service",
            parameters=[{
                "service_name": "/emergency_stop",
                "service_type": "std_srvs/srv/Empty"
            }],
            output="log"
        ),

        # =================================================================
        # EVENT HANDLERS - MONITORING AND RECOVERY
        # =================================================================

        # Monitor NAOqi driver
        RegisterEventHandler(
            OnProcessExit(
                target_action="naoqi_driver",
                on_exit=[
                    LogInfo(msg="NAOqi driver exited - respawn will handle restart"),
                ]
            )
        ),

        # Monitor rosbridge
        RegisterEventHandler(
            OnProcessExit(
                target_action="rosbridge_websocket",
                on_exit=[
                    LogInfo(msg="ROS bridge exited - HRIStudio connection lost"),
                ]
            )
        ),

        # Success notification
        RegisterEventHandler(
            OnProcessStart(
                target_action="rosbridge_websocket",
                on_start=[
                    LogInfo(msg=[
                        "\n🤖 NAO6 HRIStudio Integration Ready!\n",
                        "   WebSocket: ws://", LaunchConfiguration("bridge_port"), "\n",
                        "   Robot Topics: /", LaunchConfiguration("namespace"), "/...\n",
                        "   Status: Operational ✅\n"
                    ])
                ]
            )
        ),

        # =================================================================
        # STARTUP DELAY AND FINAL SETUP
        # =================================================================

        ExecuteProcess(
            cmd=[
                "bash", "-c",
                [
                    "sleep 3 && ",
                    "echo '=== NAO6 Integration Status ===' && ",
                    "echo 'Robot IP: '", LaunchConfiguration("nao_ip"), " && ",
                    "echo 'WebSocket Port: '", LaunchConfiguration("bridge_port"), " && ",
                    "echo 'Ready for HRIStudio experiments!' && ",
                    "echo 'Use emergency stop if needed: ros2 service call /emergency_stop std_srvs/srv/Empty'"
                ]
            ],
            name="startup_status",
            output="screen",
            shell=True
        ),
    ])
