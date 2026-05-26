import json
import redis
import time
import os
import logging
from vision_pipeline import process_sighting

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    redis_addr = os.getenv("REDIS_ADDR", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    logger.info(f"Connecting to Redis at {redis_addr}:{redis_port}")
    client = redis.Redis(host=redis_addr, port=redis_port, db=0, decode_responses=True)

    queue_name = "queue:process_sighting"
    logger.info(f"Listening on queue: {queue_name}")

    while True:
        try:
            # BLPOP blocks until a message is available
            result = client.blpop(queue_name, timeout=0)
            if result:
                _, message = result
                task = json.loads(message)
                logger.info(f"Received task for sighting: {task.get('sighting_id')}")
                
                try:
                    process_sighting(task)
                    logger.info(f"Successfully processed sighting: {task.get('sighting_id')}")
                except Exception as e:
                    logger.error(f"Error processing sighting {task.get('sighting_id')}: {e}")
        except Exception as e:
            logger.error(f"Redis connection or processing error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Wait a bit for other services to start up
    time.sleep(5)
    main()
