"""Live terminal readout of what the robot's sensors are picking up.
ros2 run roomba_sensors sensor_view"""
import math

import numpy as np
import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, Imu, LaserScan
from tf2_ros import Buffer, TransformException, TransformListener


MIN_RANGE = 0.20  # closer LiDAR hits are the robot's own body (measured up to 0.18 m)


def show(distance):
    return f'{distance:5.2f} m' if math.isfinite(distance) else 'nothing'


class SensorView(Node):
    def __init__(self):
        super().__init__('sensor_view')
        self.scan = self.imu = self.odom = None
        self.depth_center = self.depth_closest = math.inf
        self.lidar_yaw = None  # how the LiDAR is rotated on the robot
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        qos = qos_profile_sensor_data
        self.create_subscription(LaserScan, '/scan', self.on_scan, qos)
        self.create_subscription(Imu, '/imu/data', self.on_imu, qos)
        self.create_subscription(Odometry, '/odometry/filtered', self.on_odom, qos)
        self.create_subscription(Image, '/oak/stereo/depth', self.on_depth, qos)
        self.create_timer(0.25, self.report)

    def on_scan(self, msg):
        self.scan = msg

    def on_imu(self, msg):
        self.imu = msg

    def on_odom(self, msg):
        self.odom = msg

    def on_depth(self, msg):
        if msg.encoding == '32FC1':
            depth = np.frombuffer(msg.data, dtype=np.float32)
        elif msg.encoding in ('16UC1', 'mono16'):
            depth = np.frombuffer(msg.data, dtype=np.uint16).astype(np.float32) / 1000.0
            depth[depth == 0] = np.inf
        else:
            return
        depth = depth.reshape(msg.height, msg.width)
        h, w = depth.shape
        center = depth[h // 2 - 8:h // 2 + 8, w // 2 - 8:w // 2 + 8]
        center = center[np.isfinite(center) & (center > 0)]
        self.depth_center = float(np.median(center)) if center.size else math.inf
        # Ignore the bottom of the image, which is mostly the floor.
        upper = depth[:int(h * 0.6), :]
        upper = upper[np.isfinite(upper) & (upper > 0)]
        self.depth_closest = float(upper.min()) if upper.size else math.inf

    def find_lidar_yaw(self):
        if self.lidar_yaw is None and self.scan is not None:
            try:
                q = self.tf_buffer.lookup_transform(
                    'base_link', self.scan.header.frame_id, rclpy.time.Time()).transform.rotation
                self.lidar_yaw = math.atan2(2 * (q.w * q.z + q.x * q.y),
                                            1 - 2 * (q.y * q.y + q.z * q.z))
            except TransformException:
                pass

    def closest_in_direction(self, direction, half_width=math.radians(20)):
        """Closest LiDAR hit around a direction relative to the robot's front."""
        s = self.scan
        best = math.inf
        for i, r in enumerate(s.ranges):
            if not max(s.range_min, MIN_RANGE) < r < s.range_max:
                continue
            angle = s.angle_min + i * s.angle_increment + self.lidar_yaw
            difference = math.atan2(math.sin(angle - direction), math.cos(angle - direction))
            if abs(difference) <= half_width:
                best = min(best, r)
        return best

    def report(self):
        self.find_lidar_yaw()
        lines = ['ROBOT SENSORS  (Ctrl+C to quit)', '']
        if self.scan is None or self.lidar_yaw is None:
            lines.append('LiDAR: waiting for data...')
        else:
            lines += ['LiDAR: closest object in each direction',
                      f'   front {show(self.closest_in_direction(0.0))}',
                      f'   left  {show(self.closest_in_direction(math.pi / 2))}',
                      f'   right {show(self.closest_in_direction(-math.pi / 2))}',
                      f'   back  {show(self.closest_in_direction(math.pi))}']
        lines += ['', 'Depth camera:',
                  f'   straight ahead  {show(self.depth_center)}',
                  f'   closest in view {show(self.depth_closest)}', '']
        if self.imu is not None:
            lines.append(f'IMU: turning {math.degrees(self.imu.angular_velocity.z):+6.1f} deg/s')
        if self.odom is not None:
            p = self.odom.pose.pose.position
            q = self.odom.pose.pose.orientation
            heading = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
            lines += [f'Position: x {p.x:+.2f} m   y {p.y:+.2f} m   heading {math.degrees(heading):+.0f} deg',
                      f'Speed: {self.odom.twist.twist.linear.x:+.2f} m/s']
        print('\033[2J\033[H' + '\n'.join(lines), flush=True)


def main():
    rclpy.init()
    node = SensorView()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
