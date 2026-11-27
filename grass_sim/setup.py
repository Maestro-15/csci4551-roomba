from setuptools import find_packages, setup
import os
package_name = 'grass_sim'

# List of package directories
directories = [
        'config',
        'grass',
        'launch',
        'simulation',
        'worlds',
    ]

# Used to install files stored inside nested directories such as the world media file
def package_files(data_files, directory_list):
    paths_dict = {}
    for directory in directory_list:
        for path, _, filenames in os.walk(directory):
            for filename in filenames:
                if ':Zone.Identifier' in filename:
                    continue
                file_path = os.path.join(path, filename)
                install_path = os.path.join('share', package_name, path)
                if install_path in paths_dict:
                    paths_dict[install_path].append(file_path)
                else:
                    paths_dict[install_path] = [file_path]
    for key in paths_dict:
        data_files.append((key, paths_dict[key]))
    return data_files

data_files = [
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
]
package_files(data_files, directories)

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jvogel',
    maintainer_email='jvogel@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
