# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import json
import os
import re
import traceback
from threading import Thread, Timer
from time import sleep, time

import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (IoTCoreMessage,
                                            SubscriptionResponseMessage)

from src import ipc_utils
from src import utils
from src.metric.manager import MetricsManager
from src.request import PutMetricRequest


ipc = ipc_utils.IPCUtils()
config = ipc.get_configuration()

logger = utils.logger

# Setup Configuration

PUBLISH_REGION = config['PublishRegion']
PUBLISH_INTERVAL_SEC = int(config['PublishInterval'])

if PUBLISH_INTERVAL_SEC > utils.MAX_PUBLISH_INTERVAL_SEC:
    PUBLISH_INTERVAL_SEC = utils.MAX_PUBLISH_INTERVAL_SEC
    logger.info("PublishInterval can not be more than {} seconds, setting it to max value".format(str(utils.MAX_PUBLISH_INTERVAL_SEC)))

GG_CORE_NAME = os.environ.get("AWS_IOT_THING_NAME")

MAX_METRICS = int(config['MaxMetricsToRetain'])
if MAX_METRICS < utils.MIN_MAX_METRICS:
    MAX_METRICS = utils.MIN_MAX_METRICS
    logger.info("MaxMetricsToRetain can not be less than {} metrics, setting it to least value".format(str(utils.MIN_MAX_METRICS)))

INPUT_TOPIC = config['InputTopic']
if INPUT_TOPIC == "":
    INPUT_TOPIC = utils.DEFAULT_INPUT_TOPIC

OUTPUT_TOPIC = config['OutputTopic']
if OUTPUT_TOPIC == "":
    OUTPUT_TOPIC = utils.DEFAULT_OUTPUT_TOPIC

PUBSUB_TO_IOT_CORE = config['PubSubToIoTCore']

pubsub_to_iot_core = False
if re.match(r'true', str(PUBSUB_TO_IOT_CORE), flags=re.IGNORECASE):
    pubsub_to_iot_core = True

metrics_manager = MetricsManager(PUBLISH_REGION, PUBLISH_INTERVAL_SEC, MAX_METRICS)

def main():
    # Subscribe to local Pub Sub topic
    Thread(
        target = ipc.subscribe_to_pubsub_topic,
        args = (INPUT_TOPIC, PubSubStreamHandler())
    ).start()

    # Subscribe to IoT Core topic
    if pubsub_to_iot_core:
        Thread(
            target = ipc.subscribe_to_iot_topic,
            args = (INPUT_TOPIC, IoTCoreStreamHandler()) 
        ).start()



def put_metrics(metric_request):
    metric_request.add_dimension('coreName', GG_CORE_NAME)
    metrics_manager.add_metric(metric_request.namespace, metric_request.metric_datum)

class PubSubStreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            message = event.json_message.message
            logger.info("Received new message: ")
            logger.info(message)
            metric_request = PutMetricRequest(message)
            put_metrics(metric_request)
        except Exception as e:
            response = utils.generate_error_response(str(e.__class__), str(e), "")
            Thread(
                target=ipc.publish_message,
                args=(OUTPUT_TOPIC, response, pubsub_to_iot_core),
            ).start()
            logger.info(json.dumps(response))

    def on_stream_error(self, error: Exception) -> bool:
        logger.info("Received a stream error: {}".format(error))
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        logger.info("Subscribe to topic stream closed.")

class IoTCoreStreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            message = event.message.payload.decode('utf-8')
            dict_message = json.loads(message)
            logger.info("Received new message: ")
            logger.info(dict_message)
            metric_request = PutMetricRequest(dict_message)
            put_metrics(metric_request)
        except Exception as e:
            response = utils.generate_error_response(str(e.__class__), str(e), "")
            Thread(
                target = ipc.publish_message,
                args = (OUTPUT_TOPIC, response, pubsub_to_iot_core),
            ).start()
            logger.info(json.dumps(response))

    def on_stream_error(self, error: Exception) -> bool:
        logger.info("Received a stream error: {}".format(error))
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        logger.info("Subscribe to topic stream closed.")



