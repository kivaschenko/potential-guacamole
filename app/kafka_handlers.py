import asyncio
import os
import json
import logging
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaConnectionError
import time
from pydantic import BaseModel

class KafkaHandler:
    def __init__(self, loop):
        self.loop = loop
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.topic = "auth-service"
        self.producer = AIOKafkaProducer(
            loop=self.loop,
            bootstrap_servers=self.bootstrap_servers
        )

    async def start(self):
        """Start the producer"""
        await self.producer.start()

    async def stop(self):
        """Stop the producer"""
        await self.producer.stop()

    async def send_message(self, topic, message):
        """Send a message to the specified topic"""
        if isinstance(message, BaseModel):
            message = message.model_dump()
            print("Jsonify message: ", message)
        try:
            await self.producer.send_and_wait(
                topic, json.dumps(message).encode("utf-8")
            )
            logging.info(f"sent: {message}")
        except KafkaError as e:
            logging.error("error: %", e)
            raise e

    async def retry_start(self, retries=5, delay=5):
        """Retry starting the producer with a specified number of retries and delay"""
        for attempt in range(retries):
            try:
                await self.start()
                return
            except KafkaConnectionError as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise e

async def initialize_kafka_handler():
    """Initialize the Kafka handler"""
    loop = asyncio.get_event_loop()
    kafka_handler = KafkaHandler(loop)
    await kafka_handler.retry_start()
    return kafka_handler

async def produce_message(kafka_handler, topic, message):
    """Produce a message using the Kafka handler"""
    await kafka_handler.send_message(topic, message)


async def send_message_to_kafka_about_new_user(new_user):
    """Send a message to Kafka about a new user"""
    kafka_handler = await initialize_kafka_handler()
    message = {"message": "New user created", "user": new_user.model_dump_json()}
    print("Message: ", message)
    await produce_message(kafka_handler, "new-user", message)
    await kafka_handler.stop()

async def main():
    """Main function to run the Kafka producer"""
    kafka_handler = await initialize_kafka_handler()
    await produce_message(kafka_handler, "auth-service", {"message": "New message..."}) 
    await kafka_handler.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    asyncio.run(main())
