import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Package directories
    nav2_bt_project_dir = get_package_share_directory('nav2_bt_project')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')

    # Paths
    nav2_params_file = os.path.join(nav2_bt_project_dir, 'params', 'nav2_params.yaml')
    bt_xml_file = os.path.join(nav2_bt_project_dir, 'behavior_trees', 'custom_nav_tree.xml')
    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # FastDDS XML to disable shared memory transport (causes issues in containers)
    fastdds_xml = os.path.join(nav2_bt_project_dir, 'params', 'fastdds_profile.xml')

    return LaunchDescription([
        # Disable FastDDS shared memory transport
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', fastdds_xml),
        SetEnvironmentVariable('ROS_LOCALHOST_ONLY', '1'),

        # Launch arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='True',
            description='Use simulation clock'),

        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(nav2_bringup_dir, 'maps', 'turtlebot3_world.yaml'),
            description='Path to map yaml file'),

        DeclareLaunchArgument(
            'headless',
            default_value='True',
            description='Run Gazebo headless (no GUI)'),

        # 1. Launch Gazebo with TurtleBot3
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(turtlebot3_gazebo_dir, 'launch', 'turtlebot3_world.launch.py')
            ),
        ),

        # 2. Launch Nav2 localization (map_server + AMCL)
        # Delayed to let Gazebo start publishing /clock
        TimerAction(
            period=8.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(nav2_bringup_dir, 'launch', 'localization_launch.py')
                    ),
                    launch_arguments={
                        'map': map_file,
                        'use_sim_time': use_sim_time,
                        'params_file': nav2_params_file,
                    }.items(),
                ),
            ],
        ),

        # 3. Launch Nav2 navigation stack with custom BT
        # Delayed to let localization initialize
        TimerAction(
            period=15.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
                    ),
                    launch_arguments={
                        'use_sim_time': use_sim_time,
                        'params_file': nav2_params_file,
                        'default_bt_xml_filename': bt_xml_file,
                    }.items(),
                ),
            ],
        ),

        # 4. Battery simulator node
        Node(
            package='nav2_bt_project',
            executable='battery_simulator',
            name='battery_simulator',
            parameters=[{
                'use_sim_time': True,
                'initial_battery_level': 1.0,
                'drain_rate': 0.005,
                'low_battery_threshold': 0.15,
            }],
            output='screen',
        ),
    ])
