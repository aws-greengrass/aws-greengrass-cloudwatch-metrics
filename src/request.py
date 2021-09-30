# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import numbers
import time

from src.utils import *


class PutMetricRequest:

    def __init__(self, event):
        if not event:
            raise ValueError('input is empty')

        self.parse_event(event)

    def add_dimension(self, dimension_name, dimension_value):
        if self.metric_datum:
            self.metric_datum['Dimensions'].append(
                {'Name': dimension_name, 'Value': dimension_value})

    def parse_event(self, event):
        if type(event) is not dict:
            raise ValueError(
                'mandatory field ({}) is not a dict in the input'.format(FIELD_REQUEST))

        if event.get(FIELD_REQUEST) is None:
            raise ValueError(
                'mandatory field ({}) is absent in the input'.format(FIELD_REQUEST))

        self.parse_metric(event[FIELD_REQUEST])

    def parse_metric(self, metric):
        self.validate_metric(metric)

        self.namespace = metric.get(FIELD_NAMESPACE)
        self.parse_metric_datum(metric.get(FIELD_METRIC_DATA))
        self.metric_datum = {
            'MetricName': self.metric_name,
            'Value': self.metric_value,
            'Dimensions': self.dimension,
            'Unit': self.unit,
            'Timestamp': self.timestamp
        }

    def validate_metric(self, metric):
        if metric.get(FIELD_NAMESPACE) is None:
            raise ValueError(
                'mandatory field ({}) is absent in the input'.format(FIELD_NAMESPACE))

        if metric.get(FIELD_METRIC_DATA) is None:
            raise ValueError(
                'mandatory field ({}) is absent in the input'.format(FIELD_METRIC_DATA))

    def parse_metric_datum(self, metric_datum):
        self.validate_metric_datum(metric_datum)

        self.metric_name = metric_datum.get(FIELD_METRIC_NAME)
        self.metric_value = metric_datum.get(FIELD_METRIC_VALUE)
        self.unit = metric_datum.get(FIELD_METRIC_UNIT, 'Count')
        self.timestamp = metric_datum.get(FIELD_METRIC_TIMESTAMP, time.time())
        self.dimension = self.parse_dimensions(
            metric_datum.get(FIELD_DIMENSIONS))

    def validate_metric_datum(self, metric_datum):
        if type(metric_datum) is dict:
            if metric_datum.get(FIELD_METRIC_NAME) is None:
                raise ValueError(
                    'mandatory field ({}) is absent in the input'.format(FIELD_METRIC_NAME))
            if metric_datum.get(FIELD_METRIC_VALUE) is None:
                raise ValueError(
                    'mandatory field ({}) is absent in the input'.format(FIELD_METRIC_VALUE))

            if not isinstance(metric_datum.get(FIELD_METRIC_VALUE), numbers.Number):
                raise ValueError(
                    'mandatory field ({}) is not a number'.format(FIELD_METRIC_VALUE))

            if metric_datum.get(FIELD_METRIC_UNIT) and metric_datum.get(FIELD_METRIC_UNIT) not in VALID_UNIT_VALUES:
                raise ValueError(
                    'field ({}) is not a valid value, must be in ({})'.format(FIELD_METRIC_UNIT, VALID_UNIT_VALUES))

            if metric_datum.get(FIELD_METRIC_TIMESTAMP) is not None and not isinstance(
                    metric_datum.get(FIELD_METRIC_TIMESTAMP), numbers.Number):
                raise ValueError('field ({}) is not a number, must be in (milliseconds)'.format(
                    FIELD_METRIC_TIMESTAMP))

        else:
            raise ValueError(
                'Incorrect payload format, field ({}) is not a dict'.format(FIELD_METRIC_DATA))

    def parse_dimensions(self, dimensions):
        if dimensions is None:
            return []

        self.validate_dimensions(dimensions)
        return [{
            'Name': dimension.get(FIELD_DIMENSION_NAME),
            'Value': dimension.get(FIELD_DIMENSION_VALUE)
        } for dimension in dimensions]

    def validate_dimensions(self, dimensions):
        if type(dimensions) is list:
            if len(dimensions) > MAX_DIMENSIONS_PER_METRIC:
                raise ValueError(
                    'More than ({}) entries present in field ({})'.format(MAX_DIMENSIONS_PER_METRIC, FIELD_DIMENSIONS))
            for dimension in dimensions:
                if dimension.get(FIELD_DIMENSION_NAME) is None:
                    raise ValueError(
                        'mandatory field ({}) is absent in the dimension'.format(FIELD_DIMENSION_NAME))

                if dimension.get(FIELD_DIMENSION_VALUE) is None:
                    raise ValueError('mandatory field ({}) is absent in the dimension'.format(
                        FIELD_DIMENSION_VALUE))
        else:
            raise ValueError(
                'field ({}) is not of type list in the input'.format(FIELD_DIMENSIONS))
