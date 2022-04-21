from time import time, sleep
import logging
import boto3
from typing import List

# Constants
AWS_REGION = "us-east-1"
EXTRA_EC2_INSTANCES = 5
IDLE_TIME_TO_DELETE_EC2 = 120  # in seconds
SLAVE_IMAGE_AMI_ID = "ami-07c37cfe98169cdde"
REQUEST_QUEUE_NAME = "cc-project-req-sqs"
CHECK_SPAWN_CONDITION_TIME_INTERVAL = 5  # in seconds
MIN_MSGS_IN_QUEUE_TO_SPAWN_EC2 = 1

# Globals and resources
ec2 = boto3.resource('ec2')
sqs = boto3.resource('sqs', region_name=AWS_REGION)
activeEC2Instances = []

# Logging. Source: example on https://docs.python.org/3/howto/logging.html
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def spawnCondition():
    requestQueue = sqs.get_queue_by_name(QueueName=REQUEST_QUEUE_NAME)
    approximateNumberOfMessages = int(requestQueue.attributes["ApproximateNumberOfMessages"])
    logger.info("activeEC2Instances=%s" % (activeEC2Instances))
    logger.info("approximateNumberOfMessages=%d" % approximateNumberOfMessages)
    return len(activeEC2Instances) == 0 and \
        approximateNumberOfMessages >= MIN_MSGS_IN_QUEUE_TO_SPAWN_EC2


def spawnAndDelete(timeOfLastLoad):
    logger.info("Spawning extra EC2 instances ...")
    global activeEC2Instances
    for i in range(1, EXTRA_EC2_INSTANCES + 1):
        instanceName = "TestApp-instance" + str(i)
        instances = ec2.create_instances(
            ImageId=SLAVE_IMAGE_AMI_ID,
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='ec2-nvi',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instanceName
                        },
                    ]
                }
            ],
        )
        logger.info("... spawned %s." % instanceName)
        instance = instances[0]
        activeEC2Instances.append(instance)
    # Delete EC2 instances after there has been no load for a while
    timeOfLastLoad[0] = time()  # To make sure that there is some time between creating an instance and deleting it
                                # Not doing this might cause trying to delete a "Pending" instance, which will give a
                                # InvalidInstanceID.NotFound error.
    while time() - timeOfLastLoad[0] < IDLE_TIME_TO_DELETE_EC2:
        sleep(1.0)
    logger.info("There has been no load for %s secs; deleting extra instances ..." % str(IDLE_TIME_TO_DELETE_EC2))
    instanceIds = [instance.instance_id for instance in activeEC2Instances]
    ec2.instances.filter(InstanceIds=instanceIds).terminate()
    activeEC2Instances = []
    logger.info("... deleted extra instances.")


def ec2Spawner(timeOfLastLoad: List[float]):
    try:
        while True:
            logger.info("Waiting for the spawn condition ...")
            if spawnCondition():
                spawnAndDelete(timeOfLastLoad)
            sleep(CHECK_SPAWN_CONDITION_TIME_INTERVAL)
    except Exception as e:
        logger.error("Thread ec2Spawner ended with exception: " + repr(e))
