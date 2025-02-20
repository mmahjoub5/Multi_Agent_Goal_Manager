from dotenv import load_dotenv
import os 
import opik
from  shared.rabbitmq_manager import RabbitMQ_Client
from pydantic import BaseModel
import logging

# from cache.redis import RedisWrapper
# Load environment variables at the start of your application
load_dotenv()
OPENAI_KEY_CHAT = os.getenv("AZURE_OPENAI_KEY")
ENDPOINT_CHAT = os.getenv("AZURE_OPENAI_ENDPOINT")

OPENAI_KEY_COMPLETION = os.getenv("AZURE_OPENAI_KEY_2")
ENDPOINT_COMPLETION = os.getenv("AZURE_OPENAI_ENDPOINT_2")

OPENAI_GPT4_KEY = os.getenv("AZURE_OPENAI_KEY_GPT_4")
ENDPOINT_OPENAI_GPT4 = os.getenv("GPT4_ENDPOINT")

COMPLETION_VERSION = "2024-08-01-preview"  # Update if needed
 # Endpoint URL for the deployment
COMPLETION_DEPLOYMENT_NAME = "davinci-002"   # Replace with your deployed model name

# OPIK KEY 
OPIK_KEY = os.getenv('OPIK_KEY')
if not OPIK_KEY:
    raise RuntimeError("OPIK_API_KEY is not set!")
opik.configure(api_key=OPIK_KEY)
 # API version
CHAT_VERSION = "2024-08-01-preview"  # Update if needed
    # Endpoint URL for the deployment
CHAT_DEPLOYMENT_NAME = "gpt-35-turbo-16k"  # Replace with your deployed model name






if not OPENAI_KEY_CHAT or not ENDPOINT_CHAT:
    raise ValueError("Please set the AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

if not OPENAI_KEY_COMPLETION or not ENDPOINT_COMPLETION:
        raise ValueError("Please set the AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

# RabitMQ client
rabbitmq_client = RabbitMQ_Client()

#MONGO DB
MONGO_URI = "mongodb://localhost:27017" 
DATABASE_NAME = "robotarm_db"

# ROBOTTABLE = RedisWrapper()
ROBOTTABLE = {}


# API Table 
class API_CONFIG(BaseModel):
  api: str
  base_url:str
  api_version:str 
  deployment_name:str



API_TABLE = {
      "GPT4o" :  API_CONFIG(api=OPENAI_GPT4_KEY,
                            base_url=ENDPOINT_OPENAI_GPT4,
                            api_version=CHAT_VERSION,
                            deployment_name="gpt-4o"),
      "GPT3.5": API_CONFIG(api=OPENAI_KEY_CHAT,
                           base_url=ENDPOINT_CHAT,
                           api_version=CHAT_VERSION,
                           deployment_name=CHAT_DEPLOYMENT_NAME),
      "davinci-002": API_CONFIG(api=OPENAI_KEY_COMPLETION,
                                base_url=ENDPOINT_COMPLETION,
                                api_version=COMPLETION_VERSION,
                                deployment_name=COMPLETION_DEPLOYMENT_NAME)
      
}
 

logger = logging.getLogger(__name__)
