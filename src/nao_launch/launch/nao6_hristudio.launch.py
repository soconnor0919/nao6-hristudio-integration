from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    return LaunchDescription(
        [
            # NAO IP configuration
            DeclareLaunchArgument("nao_ip", default_value="nao.local"),
            DeclareLaunchArgument("nao_port", default_value="9559"),
            DeclareLaunchArgument("username", default_value="nao"),
            DeclareLaunchArgument("password", default_value="nao"),
            DeclareLaunchArgument("network_interface", default_value="eth0"),
            DeclareLaunchArgument("qi_listen_url", default_value="tcp://0.0.0.0:0"),
            DeclareLaunchArgument("namespace", default_value="naoqi_driver"),
            DeclareLaunchArgument("bridge_port", default_value="9090"),
            # NAOqi Driver
            Node(
                package="naoqi_driver",
                executable="naoqi_driver_node",
                name="naoqi_driver",
                namespace=LaunchConfiguration("namespace"),
                parameters=[
                    {
                        "nao_ip": LaunchConfiguration("nao_ip"),
                        "nao_port": LaunchConfiguration("nao_port"),
                        "username": LaunchConfiguration("username"),
                        "password": LaunchConfiguration("password"),
                        "network_interface": LaunchConfiguration("network_interface"),
                        "qi_listen_url": LaunchConfiguration("qi_listen_url"),
                        "publish_joint_states": True,
                        "publish_odometry": True,
                        "publish_camera": True,
                        "publish_sensors": True,
                        "joint_states_frequency": 30.0,
                        "odom_frequency": 30.0,
                        "camera_frequency": 15.0,
                        "sensor_frequency": 10.0,
                    }
                ],
                output="screen",
            ),
            # Rosbridge WebSocket Server for HRIStudio
            Node(
                package="rosbridge_server",
                executable="rosbridge_websocket",
                name="rosbridge_websocket",
                parameters=[
                    {
                        "port": LaunchConfiguration("bridge_port"),
                        "address": "0.0.0.0",
                        "authenticate": False,
                        "fragment_timeout": 600,
                        "delay_between_messages": 0,
                        "max_message_size": 10000000,
                    }
                ],
                output="screen",
            ),
            # ROS API Server (required for rosbridge functionality)
            Node(
                package="rosapi",
                executable="rosapi_node",
                name="rosapi",
                output="screen",
            ),
        ]
    )
