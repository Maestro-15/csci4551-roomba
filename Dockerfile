# ROS 2 Jazzy + Gazebo Harmonic on Ubuntu 24.04, for running this project on a
# machine that is not Ubuntu 24.04. On Ubuntu 24.04 you can skip Docker; see README.md.
#
#   docker build -t csci4551-roomba:jazzy .
#   ./enter.sh
FROM osrf/ros:jazzy-desktop-full

RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-jazzy-ros-gz \
      ros-jazzy-rosbot-gazebo \
      ros-jazzy-slam-toolbox \
      ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
      ros-jazzy-robot-localization \
      ros-jazzy-teleop-twist-keyboard \
      ros-jazzy-xacro \
      ros-jazzy-rqt-image-view \
      python3-colcon-common-extensions python3-numpy \
    && rm -rf /var/lib/apt/lists/*

RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc && \
    echo '[ -f /ws/install/setup.bash ] && source /ws/install/setup.bash' >> /root/.bashrc
WORKDIR /ws
