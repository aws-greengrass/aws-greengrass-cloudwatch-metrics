# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging

import boto3
from src import utils

logger = utils.logger


class CloudWatchClient:
    def __init__(self, region):
        self.client = boto3.client('cloudwatch', region)

    def put_metric_data(self, namespace, metric_data):
        put_metric_args = {'Namespace': namespace, 'MetricData': metric_data}
        try:
            response = self.client.put_metric_data(**put_metric_args)
            logger.info(
                "Cloudwatch metrics published successfully with response: {}".format(response))
            if type(response) is dict and response.get('ResponseMetadata'):
                if type(response['ResponseMetadata']) is dict and response['ResponseMetadata'].get('RequestId'):
                    return response['ResponseMetadata']['RequestId']
            # if there is no request id, just send back whole response
            return response
        except Exception as e:
            logging.error("Error was encountered publishing to cloudwatch:")
            raise
