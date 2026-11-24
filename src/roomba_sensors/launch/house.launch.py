"""ROSbot XL in the team's indoor house, driving with stop_before_hit.

    ros2 launch roomba_sensors house.launch.py
    ros2 launch roomba_sensors house.launch.py drive:=False     # drive it yourself
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription, LogInfo,
                            RegisterEventHandler)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('roomba_sensors')
    robot_sim = os.path.join(
        get_package_share_directory('rosbot_gazebo'), 'launch', 'simulation.yaml')

    activate = Node(package='roomba_sensors', executable='activate_controllers', output='screen')
    drive_node = Node(
        package='roomba_sensors', executable='stop_before_hit',
        output='log',
        condition=IfCondition(LaunchConfiguration('drive')),
    )

    def after_activation(event, _context):
        if event.returncode == 0:
            return [drive_node]
        return [LogInfo(msg='Robot was not started because its controllers are not active.')]

    return LaunchDescription([
        DeclareLaunchArgument('show_rviz', default_value='True'),
        DeclareLaunchArgument('headless', default_value='False'),
        DeclareLaunchArgument('drive', default_value='True'),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(robot_sim),
            launch_arguments={
                'robot_model': 'rosbot_xl',
                'configuration': 'autonomy',
                'gz_world': os.path.join(share, 'worlds', 'house.sdf'),
                'gz_gui': os.path.join(share, 'config', 'house_gui.config'),
                'gz_headless_mode': LaunchConfiguration('headless'),
                'rviz': 'False',
                'x': '1.2',
                'y': '-1.0',
                'z': '6.95',            # the house's ground floor is about 6.9 m up
            }.items(),
        ),
        Node(
            package='rviz2', executable='rviz2', name='sensor_rviz',
            arguments=['-d', os.path.join(share, 'config', 'sensors.rviz')],
            parameters=[{'use_sim_time': True}],
            condition=IfCondition(LaunchConfiguration('show_rviz')),
        ),
        activate,
        RegisterEventHandler(OnProcessExit(target_action=activate, on_exit=after_activation)),
    ])
