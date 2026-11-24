"""Turns on the robot's controllers if their automatic startup timed out.

The house world is heavy, so the robot's normal controller startup can fail.
This waits for the controllers to load, activates them, and then exits.
"""
import subprocess
import sys
import time

import rclpy
from builtin_interfaces.msg import Duration
from controller_manager_msgs.srv import ConfigureController, ListControllers, SwitchController
from rclpy.node import Node

CONTROLLERS = ['joint_state_broadcaster', 'imu_broadcaster', 'mecanum_drive_controller']


class ActivateControllers(Node):
    def __init__(self):
        super().__init__('activate_controllers')
        self.list_client = self.create_client(ListControllers, '/controller_manager/list_controllers')
        self.configure_client = self.create_client(
            ConfigureController, '/controller_manager/configure_controller')
        self.switch_client = self.create_client(
            SwitchController, '/controller_manager/switch_controller')

    def call(self, client, request, timeout=10.0):
        if not client.wait_for_service(timeout_sec=timeout):
            return None
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        return future.result() if future.done() else None

    def states(self):
        result = self.call(self.list_client, ListControllers.Request())
        if result is None:
            return {}
        return {c.name: c.state for c in result.controller if c.name in CONTROLLERS}

    def activate(self):
        deadline = time.monotonic() + 120.0
        while time.monotonic() < deadline and len(self.states()) < len(CONTROLLERS):
            time.sleep(1.0)
        time.sleep(8.0)     # give the normal startup a chance to finish first

        while time.monotonic() < deadline:
            states = self.states()
            if len(states) == len(CONTROLLERS) and all(s == 'active' for s in states.values()):
                return True
            for name, state in states.items():
                if state == 'unconfigured':
                    self.call(self.configure_client, ConfigureController.Request(name=name))
            waiting = [n for n, s in self.states().items() if s == 'inactive']
            if waiting:
                request = SwitchController.Request()
                request.activate_controllers = waiting
                request.strictness = SwitchController.Request.BEST_EFFORT
                request.timeout = Duration(sec=10)
                self.call(self.switch_client, request, timeout=15.0)
            time.sleep(2.0)
        return False


def main():
    rclpy.init()
    node = ActivateControllers()
    success = node.activate()
    if success:
        print('Wheel controllers are active.', flush=True)
        subprocess.run(['gz', 'service', '-s', '/gui/follow', '--reqtype', 'gz.msgs.StringMsg',
                        '--reptype', 'gz.msgs.Boolean', '--timeout', '2000',
                        '--req', 'data: "rosbot"'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        print('Could not activate the wheel controllers.', file=sys.stderr, flush=True)
    node.destroy_node()
    rclpy.try_shutdown()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
