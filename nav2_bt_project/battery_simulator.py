import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState


class BatterySimulator(Node):
    def __init__(self):
        super().__init__('battery_simulator')

        self.declare_parameter('initial_battery_level', 1.0)
        self.declare_parameter('drain_rate', 0.005)
        self.declare_parameter('low_battery_threshold', 0.15)

        self.battery_level = self.get_parameter('initial_battery_level').value
        self.drain_rate = self.get_parameter('drain_rate').value
        self.low_threshold = self.get_parameter('low_battery_threshold').value

        self.publisher_ = self.create_publisher(BatteryState, '/battery_state', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.get_logger().info(
            f'Battery simulator started: level={self.battery_level}, '
            f'drain_rate={self.drain_rate}/s, threshold={self.low_threshold}'
        )

    def timer_callback(self):
        self.battery_level = max(0.0, self.battery_level - self.drain_rate)

        msg = BatteryState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.percentage = float(self.battery_level)
        msg.voltage = float(self.battery_level * 12.6)  # Simulated voltage
        msg.present = True

        self.publisher_.publish(msg)

        if self.battery_level <= self.low_threshold and self.battery_level > 0.0:
            self.get_logger().warn(
                f'Low battery: {self.battery_level:.1%}'
            )


def main(args=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            rclpy.init(args=args)
            node = BatterySimulator()
            rclpy.spin(node)
            break
        except KeyboardInterrupt:
            break
        except (rclpy._rclpy_pybind11.RCLError,
                rclpy.executors.ExternalShutdownException) as e:
            if attempt < max_retries - 1:
                print(f'[battery_simulator] ROS context error, retrying in 2s '
                      f'(attempt {attempt + 1}/{max_retries})')
                time.sleep(2.0)
            else:
                print('[battery_simulator] Failed after all retries')
        finally:
            try:
                node.destroy_node()
            except Exception:
                pass
            try:
                rclpy.shutdown()
            except Exception:
                pass


if __name__ == '__main__':
    main()
