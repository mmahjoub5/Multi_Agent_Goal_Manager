from dotenv import load_dotenv
import os 
import opik
from ipr_worlds.shared.rabbitmq_manager import RabbitMQ_Client

# Load environment variables at the start of your application
load_dotenv()
OPENAI_KEY_CHAT = os.getenv("AZURE_OPENAI_KEY")
ENDPOINT_CHAT = os.getenv("AZURE_OPENAI_ENDPOINT")

OPENAI_KEY_COMPLETION = os.getenv("AZURE_OPENAI_KEY_2")
ENDPOINT_COMPLETION = os.getenv("AZURE_OPENAI_ENDPOINT_2")

COMPLETION_VERSION = "2024-08-01-preview"  # Update if needed
 # Endpoint URL for the deployment
COMPLETION_DEPLOYMENT_NAME = "davinci-002"   # Replace with your deployed model name

# OPIK KEY 
OPIK_KEY = os.getenv('OPIK_KEY')
opik.configure(api_key=OPIK_KEY)
 # API version
CHAT_VERSION = "2024-08-01-preview"  # Update if needed
    # Endpoint URL for the deployment
CHAT_DEPLOYMENT_NAME = "gpt-35-turbo-16k"  # Replace with your deployed model name

LLM_Config = [
  {
    "model": CHAT_DEPLOYMENT_NAME,
    "api_type": "azure",
    "api_key": OPENAI_KEY_CHAT,
    "base_url": ENDPOINT_CHAT,
    "api_version": CHAT_VERSION
  }
]




if not OPENAI_KEY_CHAT or not ENDPOINT_CHAT:
    raise ValueError("Please set the AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

if not OPENAI_KEY_COMPLETION or not ENDPOINT_COMPLETION:
        raise ValueError("Please set the AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

# RabitMQ client
rabbitmq_client = RabbitMQ_Client()

#MONGO DB
MONGO_URI = "mongodb://localhost:27017" 
DATABASE_NAME = "robotarm_db"