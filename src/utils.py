# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

PUBLISH_REGION = 'PublishRegion'
DEFAULT_PUBLISH_REGION = "us-east-1"

PUBLISH_INTERVAL_SEC = 'PublishInterval'
DEFAULT_PUBLISH_INTERVAL_SEC = 20
MAX_PUBLISH_INTERVAL_SEC = 900

MAX_METRICS = 'MaxMetricsToRetain'
DEFAULT_MAX_METRICS = 5000
MIN_MAX_METRICS = 2000

INPUT_TOPIC = 'InputTopic'
DEFAULT_INPUT_TOPIC = "cloudwatch/metric/put"
OUTPUT_TOPIC = 'OutputTopic'
DEFAULT_OUTPUT_TOPIC = "cloudwatch/metric/status"

PUBSUB_TO_IOT_CORE = 'PubSubToIoTCore'
DEFAULT_PUBSUB_TO_IOT_CORE = 'False'

GG_CORE_NAME = os.environ.get("AWS_IOT_THING_NAME")

RESPONSE = "response"
RESPONSE_FIELD_RID = "id"
RESPONSE_FIELD_STATUS = "status"
RESPONSE_FIELD_ERROR_MSG = "error_message"
RESPONSE_FIELD_ERROR_CLASS = "error"

VALUE_SUCCESS = "success"
VALUE_FAIL = "fail"

FIELD_REQUEST = "request"
FIELD_NAMESPACE = "namespace"
FIELD_METRIC_DATA = "metricData"
FIELD_METRIC_NAME = "metricName"
FIELD_METRIC_VALUE = "value"
FIELD_DIMENSIONS = "dimensions"
FIELD_DIMENSION_NAME = "name"
FIELD_DIMENSION_VALUE = "value"
FIELD_METRIC_TIMESTAMP = "timestamp"
FIELD_METRIC_UNIT = "unit"

MAX_DIMENSIONS_PER_METRIC = 10
VALID_UNIT_VALUES = {'Seconds', 'Microseconds', 'Milliseconds', 'Bytes', 'Kilobytes', 'Megabytes', 'Gigabytes',
                     'Terabytes',
                     'Bits', 'Kilobits', 'Megabits', 'Gigabits', 'Terabits', 'Percent', 'Count', 'Bytes/Second',
                     'Kilobytes/Second', 'Megabytes/Second', 'Gigabytes/Second', 'Terabytes/Second', 'Bits/Second',
                     'Kilobits/Second', 'Megabits/Second', 'Gigabits/Second', 'Terabits/Second', 'Count/Second', 'None'}


def generate_success_response(rid, **kwargs):
    success_response = {
        RESPONSE: {
            RESPONSE_FIELD_STATUS: VALUE_SUCCESS
        },
        RESPONSE_FIELD_RID: rid
    }

    if kwargs:
        success_response[RESPONSE].update(kwargs)

    return success_response


def generate_error_response(rid, error_class, error_msg, **kwargs):
    error_response = {
        RESPONSE: {
            RESPONSE_FIELD_STATUS: VALUE_FAIL,
            RESPONSE_FIELD_ERROR_MSG: error_msg,
            RESPONSE_FIELD_ERROR_CLASS: error_class
        },
        RESPONSE_FIELD_RID: rid
    }

    if kwargs:
        error_response[RESPONSE].update(kwargs)

    return error_response
