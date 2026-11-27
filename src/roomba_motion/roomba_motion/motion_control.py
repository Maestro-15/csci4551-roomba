import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Float32
SAFE_DISTANCE = 0.328 * 2
BEAMS_30_DEGREES = 250
FORWARD_SPEED = 0.7
TURN_SPEED = 0.8


class MotionControl(Node):
    def __init__(self):
        super().__init__('motion_control')
        self.create_subscription(Float32, '/front_obstacle_distance', self.frontObstacleDistace, 10)
        self.create_subscription(Float32, '/open_direction', self.openDirection, 10)
        self.create_subscription(Float32, '/low_obstacle_distance', self.onLowObstacle, 10)
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.front_obstacle_distance = 0.0 
        self.open_direction = 0.0
        self.turn_direction = None  # keeps one direction until the path is clear
        self.low_obstacle = float('inf')

    def frontObstacleDistace(self, msg):
        self.front_obstacle_distance = msg.data
        self.decide()

    def openDirection(self, msg):
        self.open_direction = msg.data

    def onLowObstacle(self, msg):
        self.low_obstacle = msg.data
        self.decide()

    def decide(self):
        cmd = TwistStamped()
        cmd.header.frame_id = 'base_link'

        if self.front_obstacle_distance < SAFE_DISTANCE or self.low_obstacle < SAFE_DISTANCE:
            if self.turn_direction is None:
                self.turn_direction = 1.0 if self.open_direction < 180 else -1.0  # + is left, - is right
            cmd.twist.angular.z = self.turn_direction * TURN_SPEED
            state = 'TURNING LEFT' if self.turn_direction > 0 else 'TURNING RIGHT'
        else:
            self.turn_direction = None
            cmd.twist.linear.x = FORWARD_SPEED
            state = 'FORWARD'

        self.publisher.publish(cmd)
        print(f'{state:13s} front {self.front_obstacle_distance:.2f} | '
              f'low {self.low_obstacle:.2f}')


def main():
    rclpy.init()
    node = MotionControl()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
