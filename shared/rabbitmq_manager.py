import pika 
import json
from pydantic import ValidationError
import threading


class RabbitMQ_Client:
    def __init__(self):
        
        # Connection parameters
        self.connection_params = pika.ConnectionParameters(
            host='localhost',
            credentials=pika.PlainCredentials('guest', 'guest')
        )
        self.connection, self.channel = self.create_connection()

    # Establish a connection and create a channel
    def create_connection(self):
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        print("RabbitMQ Connection Established")
        return connection, channel


    # Declare a queue
    def declare_queue(self,queue_name):
        self.channel.queue_declare(queue=queue_name, durable=True)
        print(f"Queue '{queue_name}' declared")

    # Send a message to a queue
    def send_message(self, queue_name, message):
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        print(f"Sent message to '{queue_name}': {message}")

    # Consume messages from a queue
    def consume_messages(self, queue_name, callback)->None:
        self.declare_queue(queue_name)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False  # We will handle acknowledgment manually
        )
        print(f"Waiting for messages in '{queue_name}'...")
        self.channel.start_consuming()

    # Acknowledge a message after processing
    def ack_message(self,delivery_tag)->None:
        self.channel.basic_ack(delivery_tag)
        print(f"Message with delivery tag {delivery_tag} acknowledged.")




class RabbitMQConsumerManager():
    def __init__(self, rabbitmq_client:RabbitMQ_Client):
        self.client = rabbitmq_client
        self.consumers = {}
        self.lock = threading.Lock()

        
    def start_consumer(self, queue_name, callback):
        if queue_name in self.consumers:
            print(f"[!] Consumer for '{queue_name}' is already running.")
            return  # Consumer for this queue is already running
        print(f"[*] Starting consumer for '{queue_name}'...")
        # Create a thread to consume messages
        thread = threading.Thread(
            target=self.client.consume_messages,
            args=(queue_name, callback),
            daemon=True
        )
        thread.start()
        self.consumers[queue_name] = thread

    def stop_consumer(self, queue_name):
        if queue_name in self.consumers:
            print(f"[*] Stopping consumer for '{queue_name}'...")
            # Terminate the thread gracefully if needed
            del self.consumers[queue_name]
        else:
            print(f"[!] No active consumer for '{queue_name}'.")
