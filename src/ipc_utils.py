# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import concurrent.futures
import json
import time
from os import getenv

import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (QOS, GetConfigurationRequest,
                                            JsonMessage, PublishMessage,
                                            PublishToIoTCoreRequest,
                                            PublishToTopicRequest,
                                            SubscribeToIoTCoreRequest,
                                            SubscribeToTopicRequest,
                                            UnauthorizedError)

from src import utils

logger = utils.logger

TIMEOUT = 10


class IPCUtils:

    def get_configuration(self):
        try:
            request = GetConfigurationRequest()
            operation = ipc_client.new_get_configuration()
            operation.activate(request).result(TIMEOUT)
            result = operation.get_response().result(TIMEOUT)
            return result.value
        except Exception as e:
            logger.error(
                "Exception occured during fetching the configuration: " + e)
            raise e

    def publish_message(self, topic, message, pubsub_to_iot_core):
        self.publish_to_pubsub_topic(topic, message)
        if pubsub_to_iot_core:
            self.publish_to_iot_topic(topic, message)

    def publish_to_pubsub_topic(self, topic, message):
        request = PublishToTopicRequest()
        request.topic = topic
        publish_message = PublishMessage()
        publish_message.json_message = JsonMessage()
        publish_message.json_message.message = message
        request.publish_message = publish_message
        operation = ipc_client.new_publish_to_topic()
        operation.activate(request)
        futureResponse = operation.get_response()
        try:
            futureResponse.result(TIMEOUT)
            logger.info('Successfully published to pubsub topic: ' + topic)
        except concurrent.futures.TimeoutError:
            logger.info(
                'Timeout occurred while publishing to pubsub topic: ' + topic)
        except UnauthorizedError as e:
            logger.error(
                'Unauthorized error while publishing to pubsub topic: ' + topic)
            raise e
        except Exception as e:
            logger.error(
                'Exception while publishing to pubsub topic: ' + topic)
            raise e

    def publish_to_iot_topic(self, topic, message):
        qos = QOS.AT_LEAST_ONCE
        request = PublishToIoTCoreRequest()
        request.topic_name = topic
        request.payload = json.dumps(message).encode('utf-8')
        request.qos = qos
        operation = ipc_client.new_publish_to_iot_core()
        operation.activate(request)
        futureResponse = operation.get_response()
        try:
            futureResponse.result(TIMEOUT)
            logger.info('Successfully published to IoT core topic: ' + topic)
        except concurrent.futures.TimeoutError:
            logger.info(
                'Timeout occurred while publishing to IoT core topic: ' + topic)
        except UnauthorizedError as e:
            logger.error(
                'Unauthorized error while publishing to IoT core topic: ' + topic)
            raise e
        except Exception as e:
            logger.error(
                'Exception while publishing to IoT core topic: ' + topic)
            raise e

    def subscribe_to_pubsub_topic(self, topic, handler):
        request = SubscribeToTopicRequest()
        request.topic = topic
        operation = ipc_client.new_subscribe_to_topic(handler)
        future = operation.activate(request)

        try:
            future.result(TIMEOUT)
            logger.info('Successfully subscribed to pubsub topic: ' + topic)
        except concurrent.futures.TimeoutError as e:
            logger.error(
                'Timeout occurred while subscribing to pubsub topic: ' + topic)
            raise e
        except UnauthorizedError as e:
            logger.error(
                'Unauthorized error while subscribing to pubsub topic: ' + topic)
            raise e
        except Exception as e:
            logger.error(
                'Exception while subscribing to pubsub topic: ' + topic)
            raise e

        # Keep the thread alive, or the process will exit.
        try:
            while True:
                time.sleep(10)
        except InterruptedError:
            logger.info('Subscribe interrupted.')

    def subscribe_to_iot_topic(self, topic, handler):
        request = SubscribeToIoTCoreRequest()
        request.topic_name = topic
        request.qos = QOS.AT_MOST_ONCE
        operation = ipc_client.new_subscribe_to_iot_core(handler)
        future = operation.activate(request)

        try:
            future.result(TIMEOUT)
            logger.info('Successfully subscribed to IoT core topic: ' + topic)
        except concurrent.futures.TimeoutError as e:
            logger.error(
                'Timeout occurred while subscribing to IoT core topic: ' + topic)
            raise e
        except UnauthorizedError as e:
            logger.error(
                'Unauthorized error while subscribing to IoT core topic: ' + topic)
            raise e
        except Exception as e:
            logger.error(
                'Exception while subscribing to IoT core topic: ' + topic)
            raise e


# Get the ipc client
try:
    ipc_client = awsiot.greengrasscoreipc.connect()
    logger.info("Created IPC client...")
except Exception as e:
    logger.error(
        "Exception occured during the creation of an IPC client: " + e
    )
    exit(1)
