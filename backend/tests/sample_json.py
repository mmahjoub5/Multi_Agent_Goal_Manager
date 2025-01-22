robot_capbilites = {
  "payload_capacity": 10.5,
  "max_speed": 2.5,
  "sensors": ["camera", "lidar", "ultrasonic"],
  "other_features": ["self-charging", "remote control"],
  "joints": [
    {
      "joint_name": "shoulder_joint",
      "joint_type": "revolute",
      "max_torque": 50.0
    },
    {
      "joint_name": "elbow_joint",
      "joint_type": "revolute",
      "max_torque": 30.0
    },
    {
      "joint_name": "wrist_joint",
      "joint_type": "prismatic",
      "max_torque": 15.0
    }
  ]
}

sample_json_1 = { "robot":
    {
  "robot_type": "robot_arm",
  "num_robots": 2,
  "robot_locations": [
    {
      "robot_id": "robot_1",
      "position": [0,0,0]
    },
    {
      "robot_id": "robot_2",
      "position": [0,0,0]
    }
  ],
  "possible_tasks": [
    {
      "task_name": "assemble",
      "task_details": "Assemble parts A and B"
    },
    {
      "task_name": "inspect",
      "task_details": "Inspect assembled parts"
    }
  ]
}
}

task_request = {
  "task": {
    "name": "Pick and Place Task",
    "robot_id": "robot_123",
    "goal_specifications": {
      "position": {"x": 1.0, "y": 2.0, "z": 3.0},
      "orientation": {"roll": 0.0, "pitch": 1.57, "yaw": 0.0},
      "tolerance": 0.01
    },
    "task_controller_type": "autogen",
    "task_description": "Move the object from point A to point B while avoiding obstacles.",
    "goals": {
      "position": {"x": 5.0, "y": 3.0, "z": 2.0},
      "orientation": {"roll": 0.0, "pitch": 1.57, "yaw": 3.14},
      "tolerance": 0.05
    }
  }
}
