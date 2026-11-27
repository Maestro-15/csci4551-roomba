import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
BEAMS_30_DEGREES = 250


class LidarWatch(Node):
    def __init__(self):
        super().__init__('lidar_watch')
        self.create_subscription(LaserScan, '/scan', self.onArrive, qos_profile_sensor_data)
        self.frontObstacle = self.create_publisher(Float32, '/front_obstacle_distance', 10)
        self.openDir = self.create_publisher(Float32, '/open_direction', 10)

    def onArrive(self, scan):
        front = scan.ranges[0]
        left = scan.ranges[750]
        back = scan.ranges[1500]
        right = scan.ranges[2250]

        ahead = scan.ranges[:BEAMS_30_DEGREES] + scan.ranges[-BEAMS_30_DEGREES:]

        big = scan.ranges.index(max(scan.ranges))
        angle = big * 0.12
        self.openDir.publish(Float32(data=angle))
        self.frontObstacle.publish(Float32(data = min(ahead)))

        print(f'closest ahead {min(ahead):.2f} | '
              f'front {front:.2f}, left {left:.2f}, back {back:.2f}, right {right:.2f}')


def main():
    rclpy.init()
    node = LidarWatch()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
