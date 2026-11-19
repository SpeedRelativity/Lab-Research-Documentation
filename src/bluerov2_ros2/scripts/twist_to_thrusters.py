#!/usr/bin/env python3
# 🔴 CRITICAL - Converts Twist to individual thruster commands

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class TwistToThrusters(Node):
    def __init__(self):
        super().__init__('twist_to_thrusters')
        
        # Subscribe to /cmd_vel
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # Publishers for each thruster
        self.thruster_pubs = []
        for i in range(1, 7):  # 6 thrusters
            pub = self.create_publisher(
                Float64,
                f'/model/bluerov2/joint/thruster{i}_joint/cmd_thrust',
                10
            )
            self.thruster_pubs.append(pub)
        
        self.get_logger().info('Twist to Thrusters converter ready!')
    
    def cmd_vel_callback(self, msg):
        """Convert Twist to thruster commands"""
        
        # Simple thruster mapping for BlueROV2
        # Thrusters 1-4: horizontal (forward/turn)
        # Thrusters 5-6: vertical (up/down)
        
        forward = msg.linear.x * 20.0   # Scale factor
        turn = msg.angular.z * 10.0
        vertical = msg.linear.z * 20.0
        
        # Calculate thruster forces
        # Front left
        t1 = forward + turn
        # Front right  
        t2 = forward - turn
        # Rear left
        t3 = forward + turn
        # Rear right
        t4 = forward - turn
        # Vertical thrusters
        t5 = vertical
        t6 = vertical
        
        thrusts = [t1, t2, t3, t4, t5, t6]
        
        # Publish to each thruster
        for i, thrust in enumerate(thrusts):
            msg = Float64()
            msg.data = float(thrust)
            self.thruster_pubs[i].publish(msg)
        
        self.get_logger().info(f'Thrusts: {[f"{t:.1f}" for t in thrusts]}')

def main():
    rclpy.init()
    converter = TwistToThrusters()
    rclpy.spin(converter)
    converter.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()