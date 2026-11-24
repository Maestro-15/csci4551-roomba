import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
SAFE_DISTANCE = 0.328 * 2
BEAMS_30_DEGREES = 250
FORWARD_SPEED = 0.2
TURN_SPEED = 0.5


class StopBeforeHit(Node):
    def __init__(self):
        super().__init__('stop_before_hit')
        self.create_subscription(LaserScan, '/scan', self.onArrive, qos_profile_sensor_data)
        self.create_subscription(Float32, '/low_obstacle_distance', self.onLowObstacle, 10)
        self.low_obstacle = float('inf')
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.turn_direction = None  # keeps one direction until the path is clear

    def onLowObstacle(self, msg):
        self.low_obstacle = msg.data

    def onArrive(self, scan):
        front = scan.ranges[0]
        left = scan.ranges[750]
        back = scan.ranges[1500]
        right = scan.ranges[2250]

        ahead = scan.ranges[:BEAMS_30_DEGREES] + scan.ranges[-BEAMS_30_DEGREES:]

        cmd = TwistStamped()
        cmd.header.frame_id = 'base_link'

        if min(ahead) < SAFE_DISTANCE or self.low_obstacle < SAFE_DISTANCE:
            if self.turn_direction is None:
                big = scan.ranges.index(max(scan.ranges))
                angle = big * 0.12
                self.turn_direction = 1.0 if angle < 180 else -1.0  # + is left, - is right
            cmd.twist.angular.z = self.turn_direction * TURN_SPEED
            state = 'TURNING LEFT' if self.turn_direction > 0 else 'TURNING RIGHT'
        else:
            self.turn_direction = None
            cmd.twist.linear.x = FORWARD_SPEED
            state = 'FORWARD'

        self.publisher.publish(cmd)
        print(f'{state:13s} closest ahead {min(ahead):.2f} | '
              f'front {front:.2f}, left {left:.2f}, back {back:.2f}, right {right:.2f}')


def main():
    rclpy.init()
    node = StopBeforeHit()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
