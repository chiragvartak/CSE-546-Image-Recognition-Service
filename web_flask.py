import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import boto3
from botocore.exceptions import ClientError
import json
import secrets
import logging

class sqs_web:
    def __init__(self):
        self.sqs = boto3.resource('sqs')
        self.logger = logging.getLogger(__name__)
        self.sqs_resources = json.load(open('resources/sqs_resources.json'))

    def push_request_to_queue(self, image):
        message_id = secrets.token_hex(16)
        try:
            response = sqs.send_message(
                QueueUrl=sqs_resources['sqs_app_queue_url'],
                DelaySeconds=10,
                MessageAttributes={
                    'request_id': {
                        'DataType': 'String',
                        'StringValue': message_id
                    }
                },
                MessageBody=image
            )
            logger.info('Request sent: %s' % response['MessageId'])

        except ClientError as error:
            logger.exception('Couldn\'t send message')
            raise error

    def pop_message_from_queue(self):
        # Need to figure this out
        return {}

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/recognise", methods=['POST'])
@cross_origin()
def recognise():
    image = body.image

    sqs_web_obj = sqs_web()
    sqs_web_obj.push_request_to_queue(image)

    response = sqs_web_obj.pop_response_from_queue()
    return jsonify({
        'something': 'something'
    })
