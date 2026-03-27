import os
from glob import glob
from setuptools import setup

package_name = 'nav2_bt_project'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'params'),
            glob('params/*.yaml') + glob('params/*.xml')),
        (os.path.join('share', package_name, 'rviz'),
            glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'maps'),
            glob('maps/*')),
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*')),
        (os.path.join('share', package_name, 'behavior_trees'),
            glob('behavior_trees/*.xml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Anthony Trieu',
    maintainer_email='ata99@sfu.ca',
    description='Nav2 BT integration for battery-aware obstacle-conscious navigation',
    license='MIT',
    entry_points={
        'console_scripts': [
            'battery_simulator = nav2_bt_project.battery_simulator:main',
        ],
    },
)
