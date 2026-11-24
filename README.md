# Automatic Floor Sweeper (CSCI 4551)

A Husarion ROSbot XL in Gazebo that drives around a room, avoids obstacles with its
LiDAR and depth camera, and builds a map with SLAM.

**Platform:** ROS 2 Jazzy, Gazebo Harmonic, Ubuntu 24.04.

## What is in here

Everything is in one package, `src/roomba_sensors`.

| Node | What it does |
|---|---|
| `stop_before_hit` | Drives forward and turns away when the LiDAR (`/scan`) or `depth_watch` sees something closer than about 0.66 m. Publishes `/cmd_vel`. |
| `depth_watch` | Reads the depth camera (`/oak/stereo/depth`), keeps points that are above the floor and in the robot's path, and publishes the closest on `/low_obstacle_distance`. Catches low objects the LiDAR misses. |
| `sensor_view` | Prints live LiDAR, depth, IMU and position readings in the terminal. |
| `activate_controllers` | Startup helper for the house world, which is heavy enough that the robot's controllers sometimes fail to start on their own. |

| Launch file | World |
|---|---|
| `obstacle_room.launch.py` | 6 x 6 m room with a few obstacles |
| `complex_room.launch.py` | 10 x 10 m room with 26 mixed obstacles, including low ones the LiDAR cannot see |
| `house.launch.py` | The team's house map. Starts `stop_before_hit` too (`drive:=False` to turn that off) |

SLAM uses `slam_toolbox` with `config/my_slam.yaml`.

## Option 1: Ubuntu 24.04 (recommended)

Works on Ubuntu 24.04, or Windows through WSL2 with Ubuntu 24.04.

1. Install ROS 2 Jazzy by following the official guide:
   https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

2. Install the robot, simulator and mapping packages:

   ```
   sudo apt update
   sudo apt install ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-rosbot-gazebo \
     ros-jazzy-slam-toolbox ros-jazzy-teleop-twist-keyboard \
     python3-colcon-common-extensions python3-numpy
   ```

3. Clone and build:

   ```
   git clone https://github.com/Maestro-15/csci4551-roomba.git
   cd csci4551-roomba
   source /opt/ros/jazzy/setup.bash
   colcon build --symlink-install
   source install/setup.bash
   ```

   Run `source /opt/ros/jazzy/setup.bash` and `source install/setup.bash` in every new terminal.

## Option 2: Docker (any Linux)

Use this if you are not on Ubuntu 24.04. The image is Ubuntu 24.04 with everything above installed.

```
git clone https://github.com/Maestro-15/csci4551-roomba.git
cd csci4551-roomba
docker build -t csci4551-roomba:jazzy .
./enter.sh
colcon build --symlink-install
source install/setup.bash
```

`./enter.sh` opens a shell in the container, or a second shell if it is already running. The
repo is mounted at `/ws`, so edits on your machine show up inside.

`enter.sh` is set up for an NVIDIA GPU. Without one, delete `--gpus all` and the three
`NVIDIA`/`__NV`/`__GLX` lines from the `docker run` command in `enter.sh`.

## Running it

Each command goes in its own terminal.

1. Start a world. Gazebo and RViz open:

   ```
   ros2 launch roomba_sensors complex_room.launch.py
   ```

2. Start low obstacle detection, then the driving node:

   ```
   ros2 run roomba_sensors depth_watch
   ```
   ```
   ros2 run roomba_sensors stop_before_hit
   ```

3. Start SLAM:

   ```
   ros2 launch slam_toolbox online_async_launch.py \
     slam_params_file:=$PWD/src/roomba_sensors/config/my_slam.yaml
   ```

   In RViz, click **Add**, then **By topic**, then **/map**. Set **Fixed Frame** to `map`, and set
   the Map display's **Durability Policy** to **Transient Local**.

To drive by keyboard instead of `stop_before_hit`:

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
```

To see how the nodes connect, run `rqt_graph`. A screenshot is in `docs/rqt_graph.png`.

## Troubleshooting

- **`Package 'roomba_sensors' not found`**: run `source install/setup.bash` in that terminal.
- **Code changes do nothing**: build with `colcon build --symlink-install`. A plain
  `colcon build` copies the code, so edits need a rebuild.
- **Robot does not move in the house world**: wait for `Wheel controllers are active.` in the
  launch output. The house world is slow to start.
- **No map in RViz**: check the Fixed Frame is `map` and the Map display uses Transient Local.

## Known limits

- The depth camera cannot see an object 7 cm tall once it is closer than about 0.54 m.
- Low obstacles avoid collisions but do not appear on the SLAM map, which uses only the LiDAR.
- Avoidance has not been tested with moving obstacles.

## AI use

Claude (an AI assistant) generated the launch files, the obstacle and complex room worlds, the
,`enter.sh`, the `Dockerfile` and this README. 
