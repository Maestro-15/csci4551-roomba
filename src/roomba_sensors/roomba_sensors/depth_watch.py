import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
import numpy as np

CAMERA_HEIGHT = 0.274
FOCAL = 1108.5
CENTER_ROW = 360
CENTER_COL = 640
CAMERA_LEFT = 0.033
CAMERA_FORWARD = -0.090
HALF_WIDTH = 0.20

class DepthWatch(Node):
    def __init__(self):
        super().__init__('depth_watch')
        self.create_subscription(Image, '/oak/stereo/depth', self.depth, qos_profile_sensor_data)
        self.publisher = self.create_publisher(Float32, '/low_obstacle_distance', 10)

    def depth(self, image):
        floats = np.frombuffer(image.data, dtype=np.float32, count=-1, offset=0)
        grid = floats.reshape(image.height, image.width)
        # row = 650
        # col =640
        # distance = grid[row, col]
        rows = np.indices(grid.shape)[0] #pixel row no.
        seen = np.isfinite(grid)
        distances = np.where(seen,grid,0)
        heights = CAMERA_HEIGHT - (rows - CENTER_ROW)/FOCAL*distances
        above_floor = seen & (heights > 0.03)
        # height = CAMERA_HEIGHT - (row- CENTER_ROW)/FOCAL*distance
        # print(f'distance {distance:.2f}, height {height:.2f}')
        # print(grid[650, 640])
        cols = np.indices(grid.shape)[1]
        sideways = CAMERA_LEFT + (CENTER_COL - cols) / FOCAL * distances #how far left or right of the robot's center each pixel is.
        in_path = np.abs(sideways) < HALF_WIDTH
        # True if that spot is within 20 cm of the center line, meaning the robot would hit it
        obstacle = above_floor & in_path
        #above the floor and in the path

        closest = float('inf')
        if obstacle.any():
            closest = float(distances[obstacle].min() + CAMERA_FORWARD)

        self.publisher.publish(Float32(data=closest))
        print(f'closest obstacle: {closest:.2f} m')

def main():
    rclpy.init()
    node = DepthWatch()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
