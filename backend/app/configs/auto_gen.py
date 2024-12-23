autogen_agent_config = {
  "agents": [
    {
      "name": "robotic_enviroment_expert",
      "type": "assistant",
      "system_message": "Your name is env expert and you are in charge of summarizing the environment for the robotics to solve a 6DOF robotics problem in the real world",
      "human_input_mode": "NEVER"
    },
    {
      "name": "robotic_controls_expert",
      "type": "conversable",
      "system_message": "Your name is control expert and you are tasked with giving the robot a list of tasks to run to complete its goal",
      "human_input_mode": "NEVER"
    },
    {
      "name": "user_proxy",
      "type": "user_proxy",
      "system_message": "You are a user proxy agent that represents the user in the environment and interacts with other agents.",
      "human_input_mode": "NEVER"
    }
  ]
}
