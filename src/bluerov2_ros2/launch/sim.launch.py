from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from pathlib import Path
import os


def generate_launch_description():
    # Workspace root
    ws = Path.home() / "rosgazebo"

    # Use the source package directly
    pkg_bluerov2 = ws / "src" / "bluerov2_ros2"

    models_path = str(pkg_bluerov2 / "models")
    worlds_path = str(pkg_bluerov2 / "worlds")
    world_file = str(pkg_bluerov2 / "worlds" / "bluerov2_underwater.world")

    # Sanity checks to catch bad paths early
    if not os.path.isdir(models_path):
        raise RuntimeError(f"Models directory not found: {models_path}")
    if not os.path.isfile(world_file):
        raise RuntimeError(f"World file not found: {world_file}")

    # Tell Gazebo where to find model:// URIs
    set_gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=models_path,
    )

    # Gazebo (server + GUI)
    gazebo = ExecuteProcess(
        cmd=[
            "gz",
            "sim",
            "-r",          # run immediately
            "-v", "4",     # verbose
            world_file,
        ],
        output="screen",
        additional_env={
            "GZ_SIM_RESOURCE_PATH": models_path,
        },
    )

    # ros_gz_bridge parameter_bridge
    bridge = Node(
    package="ros_gz_bridge",
    executable="parameter_bridge",
    arguments=[
        # Camera image (GZ <-> ROS)  — use /front_camera
        "/front_camera@sensor_msgs/msg/Image@gz.msgs.Image",

        # Thruster commands (ROS -> GZ)
        "/model/bluerov2/joint/thruster1_joint/cmd_thrust"
        "@std_msgs/msg/Float64@gz.msgs.Double",
        "/model/bluerov2/joint/thruster2_joint/cmd_thrust"
        "@std_msgs/msg/Float64@gz.msgs.Double",
        "/model/bluerov2/joint/thruster3_joint/cmd_thrust"
        "@std_msgs/msg/Float64@gz.msgs.Double",
        "/model/bluerov2/joint/thruster4_joint/cmd_thrust"
        "@std_msgs/msg/Float64@gz.msgs.Double",
        "/model/bluerov2/joint/thruster5_joint/cmd_thrust"
        "@std_msgs/msg/Float64@gz.msgs.Double",
        "/model/bluerov2/joint/thruster6_joint/cmd_thrust"
        "@std_msgs/msg/Float64@gz.msgs.Double",
    ],
    output="screen",
    )


    # Twist -> thrusters Python node (run script directly)
    twist_to_thrusters = ExecuteProcess(
        cmd=[
            "python3",
            str(pkg_bluerov2 / "twist_to_thrusters.py"),
        ],
        output="screen",
    )

    return LaunchDescription([
        set_gz_resource_path,
        gazebo,
        bridge,
        twist_to_thrusters,
    ])
