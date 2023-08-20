import os
import json
import uuid

from flask import Flask, request, jsonify, render_template

import redis

from models import Event, Session

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

EVENTS_QUEUE = os.environ.get('EVENTS_QUEUE', 'events-queue')

SOURCE = os.environ.get('APPLICATION_SOURCE', 'webhooks')

DEBUG_MODE = os.environ.get("DEBUG_MODE", 'False')
DEBUG_MODE = DEBUG_MODE.lower() == "true"

HOST = os.environ.get("HOST",'0.0.0.0')
PORT = int(os.environ.get("PORT", 5001))

app = Flask(__name__)
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/',methods=['GET'])
@app.route('/events', methods=['GET'])
def event_list():
    session = Session()
    events = session.query(Event).all()
    return render_template('index.html', events=events)

@app.route('/submit_event', methods=['POST'])
def submit_event():

    data = request.json
    user_id = data.get('UserID')
    payload = data.get('Payload')

    if user_id and payload:
        # Generate a UUID for the event ID
        event_id = str(uuid.uuid4())
        event = {}
        event['EventID'] = event_id
        event['UserID'] = user_id
        event['Payload'] = payload
        event['Source'] = SOURCE

        event_string = json.dumps(event)

        redis_client.lpush(EVENTS_QUEUE, event_string)
    
        success_message = {}
        success_message['message'] = 'Event submitted successfully'
        success_message['event_published_id'] = event_id

        return jsonify(success_message), 200
    
    else:
        return jsonify({'error': 'Invalid data'}), 400

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE, host=HOST, port=PORT)
