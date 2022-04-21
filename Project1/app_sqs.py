import boto3
import json
import logging
import time


class sqs_app:
    def __init__(self):
        self.sqs_resources = json.load(open('resources/sqs_resources.json'))
        self.sqs = boto3.resource('sqs', region_name=self.sqs_resources['sqs_region'])
        self.logger = logging.getLogger(__name__)

    def pop_request_from_queue(self):
        queue = self.sqs.get_queue_by_name(QueueName=self.sqs_resources['sqs_req_queue_name'])
        messages = queue.receive_messages(
            QueueUrl=queue.url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        if not messages:
            return None, None

        message = messages[0]
        print("Request received on TestApp: %s" % json.loads(message.body))
        self.logger.info('Request received on TestApp: %s' % message)

        return json.loads(message.body), message.receipt_handle

    def do_something_with_request(self, message):
        time.sleep(10)
        return {
            'something': 'something'
        }

    def delete_request_from_queue(self, handle):
        queue = self.sqs.get_queue_by_name(QueueName=self.sqs_resources['sqs_req_queue_name'])
        sqs_response = queue.delete_messages(
            Entries=[{
                'Id': '0',
                'ReceiptHandle': handle
            }]
        )
        print('Deleted message in TestApp: %s' % sqs_response)

    def push_response_to_queue(self, message):
        queue = self.sqs.get_queue_by_name(QueueName=self.sqs_resources['sqs_res_queue_name'])
        sqs_response = queue.send_message(
            QueueUrl=queue.url,
            DelaySeconds=0,
            MessageAttributes={},
            MessageBody=json.dumps(message)
        )

        print("Response sent from TestApp: %s" % sqs_response)
        self.logger.info('Response sent: %s' % sqs_response)


if __name__ == "__main__":
    sqs_app_obj = sqs_app()

    while True:
        request, receipt_handle = sqs_app_obj.pop_request_from_queue()
        if not request:
            continue

        response = sqs_app_obj.do_something_with_request(request)
        sqs_app_obj.delete_request_from_queue(receipt_handle)
        sqs_app_obj.push_response_to_queue({
            'message_id': request['message_id'],
            'response': response
        })
