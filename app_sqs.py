import boto3
from botocore.exceptions import ClientError

class sqs_app:
    def __init__(self):
        self.sqs_resources = json.load(open('resources/sqs_resources.json'))
        self.sqs = boto3.resource('sqs')
        self.logger = logging.getLogger(__name__)

    def pop_request_from_queue(self):
        messages = self.sqs.receive_message(
            QueueUrl=sqs_resources['sqs_app_queue_url'],
            AttributeNames=['SentTimestamp'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=['request_id'],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        request = messages['Message'][0]
        self.logger.info('Request received on app: %s' % request)
        
        return request

    def do_something_with_request(self, message):
        return {
            # Response goes here
        }

    def delete_request_from_queue(self. receipt_handle):
        self.sqs.delete_message(
            QueueUrl=sqs_resources['sqs_app_queue_url'],
            ReceiptHandle=request['RecieptHandle']
        )

    def push_response_to_queue(self.response):
        response_id = response['response_id']
        push_response = self.sqs.send_message(
            QueueUrl=sqs_resources['sqs_app_queue_url'],
            DelaySeconds=0,
            MessageAttributes={
                'response_id': {
                    'DataType': 'String',
                    'StringValue': response_id
                }
            },
            MessageBody=response['response']
        )

        self.logger.info('Response sent: %s' % push_response['MessageId'])
    
if __name__ == "__main__":
    sqs_app_obj = sqs_app()

    while True:
        request = sqs_app_obj.pop_request_from_queue()

        response = sqs_app_obj.do_something_with_request(request)
        sqs_app_obj.delete_request_from_queue(request['RecieptHandle'])
        sqs_app_obj.push_response_to_queue({
            'response_id': 'gotta be the same as request id, but different attribute name so I can filter at web'
            'response': response
        })