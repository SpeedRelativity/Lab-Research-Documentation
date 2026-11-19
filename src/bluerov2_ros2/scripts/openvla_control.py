#!/usr/bin/env python3
"""
OpenVLA ROS2 Node
Subscribes to camera, runs OpenVLA inference, publishes predicted actions
"""
import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import numpy as np
from PIL import Image as PILImage
import torch
import sys

venv_path = '/home/necharkc/openvla-study/openvla/venv'
activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.12', 'site-packages'))
# Add OpenVLA to path
sys.path.append('/home/necharkc/openvla-study/openvla')

class OpenVLANode(Node):
    def __init__(self):
        super().__init__('openvla_node')
        
        self.get_logger().info('Initializing OpenVLA Node...')
        
        # CV Bridge for ROS Image conversion
        
        # Load OpenVLA model
        self.get_logger().info('Loading OpenVLA model (this takes time)...')
        from transformers import AutoModelForVision2Seq, AutoProcessor
        
        self.processor = AutoProcessor.from_pretrained(
            "openvla/openvla-7b", 
            trust_remote_code=True
        )
        self.vla = AutoModelForVision2Seq.from_pretrained(
            "openvla/openvla-7b",
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).to("cuda" if torch.cuda.is_available() else "cpu")
        
        self.get_logger().info(f'✅ Model loaded on: {self.vla.device}')
        
        # Subscriber to camera
        self.image_sub = self.create_subscription(
            Image,
            '/front_camera',
            self.image_callback,
            10
        )
        
        # Publisher for predicted actions (for visualization)
        self.action_pub = self.create_publisher(Twist, '/openvla/predicted_action', 10)
        
        # Task prompt (what we want the robot to do)
        self.task_prompt = "navigate forward underwater"
        
        self.get_logger().info(f'✅ OpenVLA Node ready!')
        self.get_logger().info(f'Task: "{self.task_prompt}"')
        self.get_logger().info(f'Subscribed to: /front_camera')
        
        # Counter to process only every Nth frame (since CPU is slow)
        self.frame_count = 0
        self.process_every_n_frames = 30  # Process 1 out of every 30 frames
        
    def image_callback(self, msg):
        """Called when new camera image arrives"""
        self.frame_count += 1
        
        # Skip frames to avoid overload on CPU
        if self.frame_count % self.process_every_n_frames != 0:
            return
        
        self.get_logger().info(f'Processing frame {self.frame_count}...')
        
        try:
            # Convert ROS Image to OpenCV format
            # Convert ROS Image to numpy array directly (bypass cv_bridge)
            import numpy as np
            height = msg.height
            width = msg.width
            channels = 3  # RGB
            cv_image = np.frombuffer(msg.data, dtype=np.uint8).reshape(height, width, channels)
                        
            # Convert to PIL Image for OpenVLA
            pil_image = PILImage.fromarray(cv_image)
            
            # Run OpenVLA inference
            self.get_logger().info('Running OpenVLA inference (this takes time on CPU)...')
            action = self.predict_action(pil_image, self.task_prompt)
            
            self.get_logger().info(f'✅ Predicted action: {action}')
            
            # Convert action to Twist message (for visualization/future use)
            twist = self.action_to_twist(action)
            self.action_pub.publish(twist)
            
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')
    
    def predict_action(self, image, prompt):
        """Run OpenVLA inference"""
        # Prepare inputs
        inputs = self.processor(prompt, image).to(
            self.vla.device, 
            dtype=torch.bfloat16
        )
        
        # Generate action
        action = self.vla.predict_action(
            **inputs,
            unnorm_key="bridge_orig",
            do_sample=False
        )
        
        return action
    
    def action_to_twist(self, action):
        """Convert OpenVLA action to ROS Twist message"""
        # OpenVLA outputs 7D action: [x, y, z, roll, pitch, yaw, gripper]
        # We'll map to Twist: linear (x,y,z) and angular (z for yaw)
        
        twist = Twist()
        
        if len(action) >= 3:
            twist.linear.x = float(action[0])  # Forward/backward
            twist.linear.y = float(action[1])  # Left/right
            twist.linear.z = float(action[2])  # Up/down
        
        if len(action) >= 6:
            twist.angular.z = float(action[5])  # Yaw rotation
        
        return twist

def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = OpenVLANode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
