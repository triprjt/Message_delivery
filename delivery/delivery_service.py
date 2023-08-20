import multiprocessing
import os
import random
import time
import threading
import redis
import json
import uuid

from destination import SuccessDestination, FailDestination, RandomDestination
from models import Event, Session
# Read Redis host and port from environment variables or use default values
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Number of worker threads
NUM_WORKERS = 3
EVENTS_QUEUE = os.environ.get('EVENTS_QUEUE', 'events-queue')

MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))  # Maximum number of retry attempts
RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 2))  # Initial delay before first retry (in seconds)
RETRY_BACKOFF_FACTOR = int(os.environ.get('RETRY_BACKOFF_FACTOR', 2))  # Backoff factor for subsequent retries

# Destination services (mocked for demonstration)
DESTINATIONS = []

NUMBER_OF_THREADS = int(os.environ.get('NUMBER_OF_THREADS',3))

def generate_delivery_destinations():

    destination_list = []

    destination_list.append(SuccessDestination(name='Successfull destination'))
    destination_list.append(FailDestination(name='Fail destination'))
    destination_list.append(RandomDestination(name='Random success destination'))

    return destination_list

def process_event_with_retry(event, destination, retry_delay):
    try:
        session = Session()
        event = json.loads(event)
        event_id = event.get('EventID')  # Get the event ID from the event data
        event_entry = session.query(Event).filter_by(event_id=event_id).first()
        user_id = event.get('UserID')
        source = event.get('Source')
        payload = event.get('Payload')
        print("Processing event:", event_id)
        print("Delivery destination", destination.name)

        # Set the initial processing status to "Processing"
        processing_status = 'Processing'

        event_entry = None

        if event_entry:
            event_data = event_entry.event_data
            retry_attempts = event_entry.retry_attempts
            processing_status = event_entry.processing_status
        else:
            event_data = json.dumps(event)
            event_entry = Event(
                event_id=event_id,
                payload=payload,
                user_id=user_id,
                source=source,
                destination_name=destination.name,
                retry_attempts=0,
                processing_status=processing_status
            )

        session.add(event_entry)
        session.commit()

        retries = 0
        while retries <= MAX_RETRIES:
            try:
                response = destination.deliver(event)
                event_entry.retry_attempts = retries
                event_entry.response_data = json.dumps(response)
                session.commit()
                # Update the processing status based on response success
                processing_status = 'Success' if response['success'] == True else 'Failed'

                if processing_status == 'Success':
                    event_entry.processing_status = 'Success'
                    break

                retries += 1
                time.sleep(retry_delay)
                retry_delay = RETRY_DELAY * RETRY_BACKOFF_FACTOR  # Increase the delay for next retry

            except Exception as e:
                print("Error during event processing:", e)
                if retries < MAX_RETRIES:
                    retries += 1
                    print(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = RETRY_DELAY * RETRY_BACKOFF_FACTOR  # Increase the delay for next retry

        if retries >= MAX_RETRIES:
            event_entry.processing_status = 'Failed'

        event_entry.retry_attempts = retries
        session.commit()

    except Exception as e:
        print("Error setting event to 'Processing':", e)

def get_one_delivery_destination():

    number_of_destinations = len(DESTINATIONS) -1
    random_number = random.randint(0, number_of_destinations)
    return DESTINATIONS[random_number]

def worker():

    while True:
        _, event = redis_client.brpop(EVENTS_QUEUE)

        destination = get_one_delivery_destination()
        process_event_with_retry(event, destination, RETRY_DELAY)


def start_workers():
    processes = []
    for _ in range(NUMBER_OF_THREADS):
        process = multiprocessing.Process(target=worker)
        process.start()
        processes.append(process)

if __name__ == '__main__':

    DESTINATIONS = generate_delivery_destinations()
    number_of_destinations = len(DESTINATIONS)
    print("Delivery service starting")
    print(f"Number of threads: {NUMBER_OF_THREADS}")
    print(f"Number of delivery destinations: {number_of_destinations} ")
    start_workers()