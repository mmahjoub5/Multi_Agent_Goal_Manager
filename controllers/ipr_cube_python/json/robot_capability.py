import math
robot_capability_json = {
  "robot_type": "6dof_robot",
  "num_robots": 1,
  "robot_capabilities": [
    {
      "payload_capacity": 5.0,
      "max_speed": 1.0,
      "sensors": ["camera", "lidar", "force_sensor"],
      "other_features": ["gripper", "autonomous_navigation", "path_planning"],
      "joints": [
        {
          "name": "base",
          "type": "revolute",
          "bounds": [0.0, 6.0335],
          "origin_translation": [0.0, 0.0, 0.2035],
          "origin_orientation": [0.0, 0.0, 2.160746],
          "rotation": [0.0, 0.0, 1.0]
        },
        {
          "name": "upperarm",
          "type": "revolute",
          "bounds": [-2.44342, 0.0],
          "origin_translation": [0.0, 0.0, 0.0],
          "origin_orientation": [0.151362, 0.0, 0.0],
          "rotation": [-1.0, 0.0, 0.0]
        },
        {
          "name": "forearm",
          "type": "revolute",
          "bounds": [0.0, 4.2149],
          "origin_translation": [0.0, 0.0, 0.19],
          "origin_orientation": [1.024432, 0.0, 0.0],
          "rotation": [-1.0, 0.0, 0.0]
        },
        {
          "name": "wrist",
          "type": "revolute",
          "bounds": [-4.0491, 0.0],
          "origin_translation": [0.0, 0.0, 0.139],
          "origin_orientation": [0.006506, 0.0, 0.0],
          "rotation": [-1.0, 0.0, 0.0]
        },
        {
          "name": "rotational_wrist",
          "type": "revolute",
          "bounds": [-5.79789, 0.0],
          "origin_translation": [0.0, 0.0, 0.1185],
          "origin_orientation": [0.0, 0.0, 0.962531],
          "rotation": [0.0, 0.0, 1.0]
        },
        {
          "name": "gripper_right",
          "type": "revolute",
          "bounds": [0.0, 1.22171],
          "origin_translation": [0.0, 0.0, 0.0983],
          "origin_orientation": [0.0, -0.727475, 0.0],
          "rotation": [0.0, -1.0, 0.0]
        },
        {
          "name": "right_gripper_ts3_joint",
          "type": "fixed",
          "bounds": [None, None],
          "origin_translation": [0.000103, -0.000018, 0.083751],
          "origin_orientation": [-3.141593, -0.000093, -3.141593],
          "rotation": None
        }
      ]
    }
  ],
  "robot_locations": [
    {
      "robot_id": "robot_0",
      "position": [0.0, 0.0, 0.0]
    }
  ],
  "task_description": "Pick up and deliver an object",
  "environment_constraints": {
    "obstacles": "No obstacles in the path",
    "boundary": "Stay within the working area"
  },
  "goal_specifications": {
    "target_position": [1.0, 2.0, 0.5],
    "task_type": "pickup",
    "additional_parameters": {
      "object_type": "box",
      "object_weight": "2kg"
    }
  },
  "task_controller_type": "autogen"
}
