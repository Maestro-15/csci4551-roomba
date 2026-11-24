"""ROSbot XL in a simple obstacle room, with RViz showing its sensors.

    ros2 launch roomba_sensors obstacle_room.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('roomba_sensors')
    robot_sim = os.path.join(
        get_package_share_directory('rosbot_gazebo'), 'launch', 'simulation.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('show_rviz', default_value='True'),
        DeclareLaunchArgument('headless', default_value='False'),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(robot_sim),
            launch_arguments={
                'robot_model': 'rosbot_xl',
                'configuration': 'autonomy',      # LiDAR + depth camera
                'gz_world': os.path.join(share, 'worlds', 'obstacle_room.sdf'),
                'gz_gui': os.path.join(share, 'config', 'gz_gui.config'),
                'gz_headless_mode': LaunchConfiguration('headless'),
                'rviz': 'False',                  # turns off the default RViz; ours is below
            }.items(),
        ),
        Node(
            package='rviz2', executable='rviz2', name='sensor_rviz',
            arguments=['-d', os.path.join(share, 'config', 'sensors.rviz')],
            parameters=[{'use_sim_time': True}],
            condition=IfCondition(LaunchConfiguration('show_rviz')),
        ),
    ])
