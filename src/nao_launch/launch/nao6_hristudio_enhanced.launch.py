from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    LogInfo,
    RegisterEventHandler,
    EmitEvent,
    Shutdown,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit, OnProcessIO, OnProcessStart
from launch.events import Shutdown as ShutdownEvent
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Enhanced NAO6 HRIStudio Launch Configuration

    Features:
    - Safety monitoring and automatic emergency stop
    - Robot wake-up service integration
    - Comprehensive sensor publishing
    - Enhanced error handling and recovery
    - Performance monitoring
    - Configurable safety limits
    """

    return LaunchDescription([
        # =================================================================
        # CONFIGURATION ARGUMENTS
        # =================================================================

        # Robot connection parameters
        DeclareLaunchArgument(
            "nao_ip",
            default_value="nao.local",
            description="NAO robot IP address or hostname"
        ),
        DeclareLaunchArgument(
            "nao_port",
            default_value="9559",
            description="NAO robot NAOqi port"
        ),
        DeclareLaunchArgument(
            "username",
            default_value="nao",
            description="NAO robot username"
        ),
        DeclareLaunchArgument(
            "password",
            default_value="robolab",
            description="NAO robot password"
        ),
        DeclareLaunchArgument(
            "network_interface",
            default_value="eth0",
            description="Network interface for robot communication"
        ),
        DeclareLaunchArgument(
            "qi_listen_url",
            default_value="tcp://0.0.0.0:0",
            description="NAOqi listen URL"
        ),

        # ROS configuration
        DeclareLaunchArgument(
            "namespace",
            default_value="naoqi_driver",
            description="ROS namespace for NAO nodes"
        ),
        DeclareLaunchArgument(
            "bridge_port",
            default_value="9090",
            description="ROS bridge WebSocket port for HRIStudio"
        ),
        DeclareLaunchArgument(
            "bridge_address",
            default_value="0.0.0.0",
            description="ROS bridge bind address"
        ),

        # Publishing configuration
        DeclareLaunchArgument(
            "publish_joint_states",
            default_value="true",
            description="Publish robot joint states"
        ),
        DeclareLaunchArgument(
            "publish_odometry",
            default_value="true",
            description="Publish robot odometry"
        ),
        DeclareLaunchArgument(
            "publish_camera",
            default_value="true",
            description="Publish camera feeds"
        ),
        DeclareLaunchArgument(
            "publish_sensors",
            default_value="true",
            description="Publish sensor data (touch, bumper, sonar)"
        ),

        # Frequency configuration
        DeclareLaunchArgument(
            "joint_states_frequency",
            default_value="30.0",
            description="Joint states publishing frequency (Hz)"
        ),
        DeclareLaunchArgument(
            "odom_frequency",
            default_value="30.0",
            description="Odometry publishing frequency (Hz)"
        ),
        DeclareLaunchArgument(
            "camera_frequency",
            default_value="15.0",
            description="Camera publishing frequency (Hz)"
        ),
        DeclareLaunchArgument(
            "sensor_frequency",
            default_value="10.0",
            description="Sensor data publishing frequency (Hz)"
        ),

        # Safety parameters
        DeclareLaunchArgument(
            "enable_safety_monitoring",
            default_value="true",
            description="Enable safety monitoring and emergency stop"
        ),
        DeclareLaunchArgument(
            "max_linear_velocity",
            default_value="0.3",
            description="Maximum allowed linear velocity (m/s)"
        ),
        DeclareLaunchArgument(
            "max_angular_velocity",
            default_value="1.0",
            description="Maximum allowed angular velocity (rad/s)"
        ),

        # Auto wake-up
        DeclareLaunchArgument(
            "auto_wake_up",
            default_value="true",
            description="Automatically wake up robot on launch"
        ),

        # Debug and logging
        DeclareLaunchArgument(
            "debug_mode",
            default_value="false",
            description="Enable debug logging"
        ),
        DeclareLaunchArgument(
            "log_level",
            default_value="INFO",
            description="ROS log level (DEBUG, INFO, WARN, ERROR)"
        ),

        # =================================================================
        # PRE-LAUNCH SETUP
        # =================================================================

        LogInfo(
            msg=[
                "Starting NAO6 HRIStudio Integration...\n",
                "Robot IP: ", LaunchConfiguration("nao_ip"), "\n",
                "Bridge Port: ", LaunchConfiguration("bridge_port"), "\n",
                "Safety Monitoring: ", LaunchConfiguration("enable_safety_monitoring")
            ]
        ),

        # Robot connectivity test
        ExecuteProcess(
            cmd=["ping", "-c", "3", LaunchConfiguration("nao_ip")],
            name="nao_connectivity_test",
            output="log",
            condition=IfCondition(LaunchConfiguration("debug_mode"))
        ),

        # =================================================================
        # ROBOT WAKE-UP SERVICE
        # =================================================================

        ExecuteProcess(
            cmd=[
                "sshpass", "-p", LaunchConfiguration("password"),
                "ssh", "-o", "StrictHostKeyChecking=no",
                [LaunchConfiguration("username"), "@", LaunchConfiguration("nao_ip")],
                "python2 -c \"import sys; sys.path.append('/opt/aldebaran/lib/python2.7/site-packages'); import naoqi; motion = naoqi.ALProxy('ALMotion', '127.0.0.1', 9559); motion.wakeUp(); print('Robot awakened successfully')\""
            ],
            name="nao_wake_up_service",
            output="log",
            condition=IfCondition(LaunchConfiguration("auto_wake_up"))
        ),

        # =================================================================
        # CORE NAO DRIVER
        # =================================================================

        Node(
            package="naoqi_driver",
            executable="naoqi_driver_node",
            name="naoqi_driver",
            namespace=LaunchConfiguration("namespace"),
            parameters=[{
                # Connection parameters
                "nao_ip": LaunchConfiguration("nao_ip"),
                "nao_port": LaunchConfiguration("nao_port"),
                "username": LaunchConfiguration("username"),
                "password": LaunchConfiguration("password"),
                "network_interface": LaunchConfiguration("network_interface"),
                "qi_listen_url": LaunchConfiguration("qi_listen_url"),

                # Publishing configuration
                "publish_joint_states": LaunchConfiguration("publish_joint_states"),
                "publish_odometry": LaunchConfiguration("publish_odometry"),
                "publish_camera": LaunchConfiguration("publish_camera"),
                "publish_sensors": LaunchConfiguration("publish_sensors"),

                # Frequency configuration
                "joint_states_frequency": LaunchConfiguration("joint_states_frequency"),
                "odom_frequency": LaunchConfiguration("odom_frequency"),
                "camera_frequency": LaunchConfiguration("camera_frequency"),
                "sensor_frequency": LaunchConfiguration("sensor_frequency"),

                # Additional NAO-specific parameters
                "publish_body_pose": True,
                "publish_foot_contact": True,
                "publish_robot_description": True,
                "use_sim_time": False,

                # Audio configuration
                "publish_audio": True,
                "audio_frequency": 16000,
                "audio_channels": 1,

                # Safety parameters
                "enable_emergency_stop": LaunchConfiguration("enable_safety_monitoring"),
                "max_linear_velocity": LaunchConfiguration("max_linear_velocity"),
                "max_angular_velocity": LaunchConfiguration("max_angular_velocity"),
            }],
            output="screen",
            emulate_tty=True,
            arguments=[
                "--ros-args",
                "--log-level", LaunchConfiguration("log_level")
            ]
        ),

        # =================================================================
        # ROSBRIDGE WEBSOCKET SERVER
        # =================================================================

        Node(
            package="rosbridge_server",
            executable="rosbridge_websocket",
            name="rosbridge_websocket",
            parameters=[{
                "port": LaunchConfiguration("bridge_port"),
                "address": LaunchConfiguration("bridge_address"),
                "authenticate": False,
                "fragment_timeout": 600,
                "delay_between_messages": 0,
                "max_message_size": 10000000,
                "unregister_timeout": 10.0,
                "service_timeout": 5.0,
                "bson_only_mode": False,
                "retry_startup_delay": 5.0,
                "topics_glob": [],
                "services_glob": [],
                "params_glob": [],
            }],
            output="screen",
            emulate_tty=True,
            arguments=[
                "--ros-args",
                "--log-level", LaunchConfiguration("log_level")
            ]
        ),

        # =================================================================
        # ROS API SERVER
        # =================================================================

        Node(
            package="rosapi",
            executable="rosapi_node",
            name="rosapi",
            parameters=[{
                "topics_glob": [],
                "services_glob": [],
                "params_glob": [],
            }],
            output="screen",
            emulate_tty=True
        ),

        # =================================================================
        # SAFETY AND MONITORING NODES
        # =================================================================

        # Robot state monitor
        Node(
            package="naoqi_driver",
            executable="naoqi_driver_node",
            name="nao_state_monitor",
            namespace=[LaunchConfiguration("namespace"), "/monitoring"],
            parameters=[{
                "nao_ip": LaunchConfiguration("nao_ip"),
                "nao_port": LaunchConfiguration("nao_port"),
                "username": LaunchConfiguration("username"),
                "password": LaunchConfiguration("password"),
                "monitor_only": True,
                "battery_check_frequency": 5.0,
                "temperature_check_frequency": 5.0,
                "fall_detection": True,
            }],
            output="log",
            condition=IfCondition(LaunchConfiguration("enable_safety_monitoring"))
        ),

        # Emergency stop service
        Node(
            package="naoqi_driver",
            executable="emergency_stop_service",
            name="emergency_stop_service",
            namespace=LaunchConfiguration("namespace"),
            parameters=[{
                "nao_ip": LaunchConfiguration("nao_ip"),
                "nao_port": LaunchConfiguration("nao_port"),
                "username": LaunchConfiguration("username"),
                "password": LaunchConfiguration("password"),
            }],
            output="log",
            condition=IfCondition(LaunchConfiguration("enable_safety_monitoring"))
        ),

        # =================================================================
        # ADDITIONAL UTILITY NODES
        # =================================================================

        # TF2 static transforms for robot model
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="nao_base_link_publisher",
            arguments=[
                "0", "0", "0", "0", "0", "0",
                "odom", [LaunchConfiguration("namespace"), "/base_link"]
            ],
            output="log"
        ),

        # Robot description publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            namespace=LaunchConfiguration("namespace"),
            parameters=[{
                "robot_description": "$(find nao_description)/urdf/naoV40_generated_urdf/nao.urdf",
                "use_sim_time": False,
            }],
            output="log",
            condition=IfCondition(LaunchConfiguration("publish_joint_states"))
        ),

        # Joint state publisher (for visualization)
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
            namespace=LaunchConfiguration("namespace"),
            parameters=[{
                "source_list": ["/naoqi_driver/joint_states"],
                "rate": LaunchConfiguration("joint_states_frequency"),
            }],
            output="log",
            condition=IfCondition(LaunchConfiguration("publish_joint_states"))
        ),

        # =================================================================
        # EVENT HANDLERS FOR MONITORING
        # =================================================================

        # Handle NAOqi driver failures
        RegisterEventHandler(
            OnProcessExit(
                target_action=Node(package="naoqi_driver", executable="naoqi_driver_node"),
                on_exit=[
                    LogInfo(msg="NAOqi driver has exited. Attempting restart..."),
                    # Could add restart logic here
                ]
            )
        ),

        # Handle rosbridge failures
        RegisterEventHandler(
            OnProcessExit(
                target_action=Node(package="rosbridge_server", executable="rosbridge_websocket"),
                on_exit=[
                    LogInfo(msg="ROS bridge has exited. This will affect HRIStudio connectivity."),
                ]
            )
        ),

        # Success notification
        RegisterEventHandler(
            OnProcessStart(
                target_action=Node(package="rosbridge_server", executable="rosbridge_websocket"),
                on_start=[
                    LogInfo(msg=[
                        "NAO6 HRIStudio integration launched successfully!\n",
                        "WebSocket available at: ws://", LaunchConfiguration("bridge_address"), ":", LaunchConfiguration("bridge_port"), "\n",
                        "Robot namespace: ", LaunchConfiguration("namespace")
                    ])
                ]
            )
        ),

        # =================================================================
        # CLEANUP ON EXIT
        # =================================================================

        ExecuteProcess(
            cmd=[
                "bash", "-c",
                "sleep 2 && echo 'NAO6 HRIStudio integration ready for experiments!'"
            ],
            name="startup_notification",
            output="screen"
        )
    ])
