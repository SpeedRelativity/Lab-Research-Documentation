
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class SimpleROVControl(Node):
    def __init__(self):
        super().__init__('simple_rov_control')  # Node name
        
        # Create a publisher
        self.vel_pub = self.create_publisher(
            Twist,              # Message type
            '/cmd_vel',         # Topic name (matches bridge!)
            10                  # Queue size
        )
        
        self.get_logger().info('Simple ROV Control initialized!')


    z: 0.0     # Yaw - rotation left/right


    def move(self, linear_x=0.0, linear_y=0.0, linear_z=0.0, angular_z=0.0):
        """Send a velocity command"""
        
        # Create the message
        msg = Twist()
        msg.linear.x = linear_x    # Forward/backward speed (m/s)
        msg.linear.y = linear_y    # Left/right speed (m/s)
        msg.linear.z = linear_z    # Up/down speed (m/s)
        msg.angular.z = angular_z  # Rotation speed (rad/s)
        
        # Publish it
        self.vel_pub.publish(msg)
        
        self.get_logger().info(
            f'Sent: linear=[{linear_x}, {linear_y}, {linear_z}], angular_z={angular_z}'
        )


def main():
    # Initialize ROS2
    rclpy.init()
    
    # Create our node
    controller = SimpleROVControl()
    
    # Give the bridge time to connect
    time.sleep(2)
    
    # Test movements
    controller.get_logger().info('=== Starting movement test ===')
    
    # Move forward for 3 seconds
    controller.get_logger().info('Moving forward...')
    controller.move(linear_x=0.5)  # 0.5 m/s forward
    time.sleep(3)
    
    # Stop
    controller.move()  # All zeros = stop
    time.sleep(1)
    
    # Move backward
    controller.get_logger().info('Moving backward...')
    controller.move(linear_x=-0.5)  # Negative = backward
    time.sleep(3)
    
    # Stop
    controller.move()
    time.sleep(1)
    
    # Move up
    controller.get_logger().info('Moving up...')
    controller.move(linear_z=0.3)  # Positive Z = up
    time.sleep(3)
    
    # Stop
    controller.move()
    time.sleep(1)
    
    # Rotate
    controller.get_logger().info('Rotating...')
    controller.move(angular_z=0.5)  # Rotate counterclockwise
    time.sleep(3)
    
    # Stop
    controller.move()
    
    controller.get_logger().info('=== Test complete! ===')
    
    # Cleanup
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()