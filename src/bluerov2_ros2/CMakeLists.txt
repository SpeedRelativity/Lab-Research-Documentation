cmake_minimum_required(VERSION 3.8)
project(bluerov2_ros2)

find_package(ament_cmake REQUIRED)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

install(PROGRAMS
  scripts/simple_control.py
  scripts/twist_to_thrusters.py
  scripts/openvla_control.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install models and worlds
install(DIRECTORY
  models
  worlds
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
