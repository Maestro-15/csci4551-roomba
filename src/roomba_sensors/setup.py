from glob import glob

from setuptools import find_packages, setup

package_name = 'roomba_sensors'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
        ('share/' + package_name + '/config', glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'activate_controllers = roomba_sensors.activate_controllers:main',
            'sensor_view = roomba_sensors.sensor_view:main',
            'lidar_watch = roomba_sensors.lidar_watch:main',
                'depth_watch = roomba_sensors.depth_watch:main',
        ],
    },
)
