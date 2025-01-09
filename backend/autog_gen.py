import os

from autogen import ConversableAgent
from dotenv import load_dotenv

from app.main import Enviroment, templateManager
import os
from dotenv import load_dotenv
from app.templates import example_strings
json = {
    "robotLinks": [1,2,3],
    "goalPosition": [0,0,0],
    "NumberOfRobots": 3,
    "initialPositions": [0,10,1]
}
environment = Enviroment(**json)
print(environment.model_dump())




prompt = templateManager(environment=environment.model_dump() , 
                        tasks=["go up", "go left", "go right", "go down"],
                        example_one= example_strings.example1_prompt,
                        example_two = example_strings.example2_prompt

                         )
print(prompt)


#Load environment variables at the start of your application
load_dotenv("ipr_worlds/backend/app/.env")
OPENAI_KEY_CHAT = os.getenv("AZURE_OPENAI_KEY")
ENDPOINT_CHAT = os.getenv("AZURE_OPENAI_ENDPOINT")
CHAT_VERSION = "2024-08-01-preview"  # Update if needed

LLM_Config = [
  {
    "model": "gpt-35-turbo-16k",
    "api_type": "azure",
    "api_key": OPENAI_KEY_CHAT,
    "base_url": ENDPOINT_CHAT,
    "api_version": CHAT_VERSION
  }
]


env_expert = ConversableAgent(
    "robotic_enviroment_expert",
    system_message="Your name is env expert and are in charge of summarizing the enviroment for the robotics to solve a 6DOF robotics problem in the real world",
    llm_config={"config_list": LLM_Config},
    human_input_mode="NEVER",  # Never ask for human input.
)


control_expert = ConversableAgent(
    name="robotic_controls_expert",
    system_message="Your name is control expert are tasked with giving the robot a list of tasks to run to completes it goal",
    llm_config={"config_list": LLM_Config},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)

result = env_expert.initiate_chat(control_expert, message=prompt, max_turns=4)

