import secrets
import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import boto3
from botocore.exceptions import ClientError
import json
import logging
import threading
import time
import os
import base64

lock = threading.Lock()


class sqs_web:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sqs_resources = json.load(open('resources/sqs_resources.json'))
        self.sqs = boto3.resource('sqs', region_name=self.sqs_resources['sqs_region'])
        self.message_id = secrets.token_hex(16)

    def push_request_to_queue(self, image):
        encoded_image = base64.b64encode(image).decode('utf-8')
        try:
            queue = self.sqs.get_queue_by_name(QueueName=self.sqs_resources['sqs_req_queue_name'])
            sqs_response = queue.send_message(
                QueueUrl=queue.url,
                DelaySeconds=10,
                MessageAttributes={},
                MessageBody=json.dumps({
                    'message_id': self.message_id,
                    'image': encoded_image
                })
            )
            print('Request sent: %s' % sqs_response, flush=True)
            self.logger.info('Request sent from web: %s' % sqs_response['MessageId'])

        except ClientError as error:
            self.logger.exception('Couldn\'t send message')
            raise error

    def delete_response_from_queue(self, handle):
        queue = self.sqs.get_queue_by_name(QueueName=self.sqs_resources['sqs_res_queue_name'])
        sqs_response = queue.delete_messages(
            Entries=[{
                'Id': '0',
                'ReceiptHandle': handle
            }]
        )
        print('Deleted message in web: %s' % sqs_response, flush=True)

    def pop_response_from_queue(self):
        queue = self.sqs.get_queue_by_name(QueueName=self.sqs_resources['sqs_res_queue_name'])
        messages = queue.receive_messages(
            QueueUrl=queue.url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=15,
            MessageAttributeNames=['All'],
        )

        response = None
        write_flag = False
        if messages:
            write_flag = True

        with lock:
            with open('resources/response_map.json', 'r') as response_map_file:
                response_map = json.load(response_map_file)

            if self.message_id in response_map:
                response = response_map[self.message_id]
                response_map.pop(self.message_id, None)
                write_flag = True

            for message in messages:
                message_body = json.loads(message.body)

                print('Response received on web: %s' % json.loads(message.body), flush=True)
                self.logger.info('Response received on web: %s' % json.loads(message.body))

                self.delete_response_from_queue(message.receipt_handle)

                if message_body['message_id'] == self.message_id:
                    response = message_body['response']
                else:
                    response_map[message_body['message_id']] = message_body['response']

            if write_flag:
                with open('resources/response_map.json', 'w') as response_map_file:
                    json.dump(response_map, response_map_file)

        return response


app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

if not os.path.isfile('./resources/response_map.json'):
    print('Creating global response map', flush=True)
    with lock:
        response_map = {}
        with open('./resources/response_map.json', 'w+') as response_map_file:
            json.dump(response_map, response_map_file)


@app.route("/recognize", methods=['POST'])
@cross_origin()
def recognise():
    image = request.files['myfile'].read()

    sqs_web_obj = sqs_web()
    sqs_web_obj.push_request_to_queue(image)

    while True:
        response = sqs_web_obj.pop_response_from_queue()
        if response:
            return jsonify(response)

        time.sleep(15)
