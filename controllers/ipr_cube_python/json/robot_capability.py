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
  "task_description": "Pick up objectand deliver an object",
  "environment_constraints": {
    "obstacles": "No obstacles in the path",
    "boundary": "Stay within the working area"
  },
  "goal_specifications": {
    "target_position": [3.44e-5, -.30, 0],
    "task_type": "pickup",
    "additional_parameters": {
      "object_type": "box",
      "object_weight": "2kg"
    }
  },
  "task_controller_type": "autogen",
  "possible_tasks": 
                   [
                        {
                            "task_name": "move_base",
                            "parameters": "[value: float (in radians)]",
                            "description": "Moves the robot's base joint to the specified position in radians. The value parameter is a float representing the position of the base joint in radians."
                        },
                        {
                            "task_name": "move_upperarm",
                            "parameters": "[value: float (in radians)]",
                            "description": "Moves the robot's upper arm joint to the specified position in radians. The value parameter is a float representing the position of the upper arm joint in radians."
                        },
                        {
                            "task_name": "move_forearm",
                            "parameters": ["value: float (in radians)"],
                            "description": "Moves the robot's forearm joint to the specified position in radians. The value parameter is a float representing the position of the forearm joint in radians."
                        },
                        {
                            "task_name": "move_wrist",
                            "parameters": ["value: float (in radians)"],
                            "description": "Moves the robot's wrist joint to the specified position in radians. The value parameter is a float representing the position of the wrist joint in radians."
                        },
                        {
                            "task_name": "move_rotational_wrist",
                            "parameters": ["value: float (in radians)"],
                            "description": "Moves the robot's rotational wrist joint to the specified position in radians. The value parameter is a float representing the position of the rotational wrist joint in radians."
                        },
                        {
                            "task_name": "move_gripper_right",
                            "parameters": ["value: float (in radians)"],
                            "description": "Moves the robot's gripper to the specified position in radians. The value parameter is a float representing the position of the gripper in radians."
                        },
                        {
                          "task_name": "move_all_joints_to_init",
                          "parameters": "[]",
                          "description": "Moves all the robot joints to their initial position. No parameters are required."
                        },
                        {
                            "task_name": "grab_object",
                            "parameters": "[grab_position: list[float] (in radians)]",
                            "description": "Instructs the robot to grab an object at the specified position. The grab_position parameter is a list of 6 floats specficing the joint positions in radians"
                        },
                        {
                            "task_name": "drop_object",
                            "parameters": ["drop_position: list[float] (in radians)"],
                            "description": "Instructs the robot to grab an object at the specified position. The drop_position parameter is a list of 6 floats specficing the joint positions in radians"
                        },
                        {
                            "task_name": "calculate_forward_kinematics",
                            "parameters": ["joint_angles: list[float] (in radians)"],
                            "description": "Calculates the forward kinematics for the robot based on the given joint angles. The joint_angles parameter is a list of floats representing the joint angles of the robot in radians."
                        },
                        {
                          "task_name": "calculate_inverse_kinematics",
                          "parameters": "[ target_position: list[float] (in meters),  // target position [x, y, z] target_orientation: list[float] (in radians), initial_angles: list[float] (in radians)  // initial joint angles]",
                          "description": "Calculates the inverse kinematics of the robot based on the target position (in meters), orientation (in radians), and initial angles (in radians). Function returns position for all motors."
                        }
                     ]
                    
}
