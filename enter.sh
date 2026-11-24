#!/bin/bash
cd "$(dirname "$0")"
SETUP='source /opt/ros/jazzy/setup.bash; [ -f install/setup.bash ] && source install/setup.bash; exec bash'
if docker ps --format '{{.Names}}' | grep -qx roomba; then
  exec docker exec -it roomba bash -c "$SETUP"
fi
exec docker run -it --rm --name roomba --net host --ipc host --gpus all \
  -e NVIDIA_DRIVER_CAPABILITIES=all -e __NV_PRIME_RENDER_OFFLOAD=1 -e __GLX_VENDOR_LIBRARY_NAME=nvidia \
  --user "$(id -u):$(id -g)" -e HOME=/ws/.home -e DISPLAY="$DISPLAY" -e GZ_IP=127.0.0.1 \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v "$PWD":/ws -w /ws \
  csci4551-roomba:jazzy bash -c "$SETUP"
