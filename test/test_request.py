# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

import pytest

from src.request import *

DEFAULT_NAMESPACE = 'Greengrass'
DEFAULT_METRIC_NAME = 'Count'
DEFAULT_METRIC_VALUE = 12.0
DEFAULT_METRIC_UNITS = 'Seconds'
DEFAULT_DIMENSION_NAME = 'hostname'
DEFAULT_DIMENSION_VALUE = 'test_hostname'


class TestPutMetricRequest(object):

    def assert_default_metric_values(self, metric_datum):
        assert metric_datum['Value'] == DEFAULT_METRIC_VALUE
        assert metric_datum['MetricName'] == DEFAULT_METRIC_NAME
        assert metric_datum['Unit'] == DEFAULT_METRIC_UNITS
        assert metric_datum['Dimensions'][0]['Name'] == DEFAULT_DIMENSION_NAME
        assert metric_datum['Dimensions'][0]['Value'] == DEFAULT_DIMENSION_VALUE

    def test_successful_parse_request(self):
        event = self.create_valid_request_with_all_fields()

        put_request = PutMetricRequest(event)

        assert put_request.namespace == DEFAULT_NAMESPACE
        self.assert_default_metric_values(put_request.metric_datum)

    def test_parse_fails_with_empty_input(self):
        with pytest.raises(Exception) as error:
            PutMetricRequest("")

        assert 'input is empty' in str(error.value)

    def test_parse_fails_with_no_request_field(self):
        with pytest.raises(Exception) as error:
            PutMetricRequest({'Random': 'test'})

        assert 'mandatory field ({}) is absent in the input'.format(FIELD_REQUEST) in str(error.value)

    def test_parse_fails_with_request_field_is_not_dict(self):
        with pytest.raises(Exception) as error:
            PutMetricRequest("test")

        assert 'mandatory field ({}) is not a dict in the input'.format(FIELD_REQUEST) in str(error.value)

    def test_parse_request_fails_when_timestamp_is_not_number(self):
        event = self.create_valid_request_with_all_fields()
        event['request']['metricData']['timestamp'] = 'Wed, 24 Jun 2020 14:09:19 UTC'

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'field ({}) is not a number, must be in (milliseconds)'.format(FIELD_METRIC_TIMESTAMP) in str(
            error.value)

    def test_add_dimension(self):
        event = self.create_valid_request_with_all_fields()

        put_request = PutMetricRequest(event)
        put_request.add_dimension('TestName', 'TestValue')

        assert put_request.namespace == DEFAULT_NAMESPACE
        assert put_request.metric_datum['Dimensions'][1]['Name'] == 'TestName'
        assert put_request.metric_datum['Dimensions'][1]['Value'] == 'TestValue'

        # clear out dimension array
        del event['request']['metricData']['dimensions'][:]
        put_request = PutMetricRequest(event)
        put_request.add_dimension('TestName', 'TestValue')

        assert put_request.namespace == DEFAULT_NAMESPACE
        assert put_request.metric_datum['Dimensions'][0]['Name'] == 'TestName'
        assert put_request.metric_datum['Dimensions'][0]['Value'] == 'TestValue'

        # remove the dimension array
        del event['request']['metricData']['dimensions']
        put_request = PutMetricRequest(event)
        put_request.add_dimension('TestName', 'TestValue')

        assert put_request.namespace == DEFAULT_NAMESPACE
        assert put_request.metric_datum['Dimensions'][0]['Name'] == 'TestName'
        assert put_request.metric_datum['Dimensions'][0]['Value'] == 'TestValue'

    def test_parse_request_success_when_dimensions_empty(self):
        event = self.create_valid_request_with_all_fields()
        # clear out the dimension array
        del event['request']['metricData']['dimensions'][:]
        print(event)

        put_request = PutMetricRequest(event)
        assert put_request.namespace == DEFAULT_NAMESPACE
        assert len(put_request.metric_datum['Dimensions']) == 0

    def test_parse_request_success_when_dimensions_absent(self):
        event = self.create_valid_request_with_all_fields()
        # remove the dimension array
        del event['request']['metricData']['dimensions']
        print(event)

        put_request = PutMetricRequest(event)
        assert put_request.namespace == DEFAULT_NAMESPACE
        assert len(put_request.metric_datum['Dimensions']) == 0

    def test_successful_parse_request_with_multiple_dimensions(self):
        event = self.create_valid_request_with_all_fields()
        new_dimension = {'name': 'new_name', 'value': 'new_value'}
        event['request']['metricData']['dimensions'].append(new_dimension)

        put_request = PutMetricRequest(event)
        put_request_metric_datum = put_request.metric_datum

        self.assert_default_metric_values(put_request_metric_datum)
        assert put_request_metric_datum['Dimensions'][1].get('Name') == 'new_name'
        assert put_request_metric_datum['Dimensions'][1].get('Value') == 'new_value'

    def test_parse_request_fails_when_dimensions_exceed_limit(self):
        event = self.create_valid_request_with_all_fields()
        new_dimension = {'name': 'new_name', 'value': 'new_value'}
        event['request']['metricData']['dimensions'].extend([new_dimension, new_dimension, new_dimension,
                                                             new_dimension, new_dimension, new_dimension,
                                                             new_dimension, new_dimension, new_dimension,
                                                             new_dimension])

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'More than ({}) entries present in field (dimensions)'.format(MAX_DIMENSIONS_PER_METRIC) in str(
            error.value)

    def test_parse_request_fails_when_dimensions_name_absent(self):
        event = self.create_valid_request_with_all_fields()
        del event['request']['metricData']['dimensions'][0]['name']

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'mandatory field ({}) is absent in the dimension'.format(FIELD_DIMENSION_NAME) in str(error.value)

    def test_parse_request_fails_when_dimensions_is_not_dict(self):
        event = self.create_valid_request_with_all_fields()
        event['request']['metricData']['dimensions'] = {}

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'field ({}) is not of type list in the input'.format(FIELD_DIMENSIONS) in str(error.value)

        event['request']['metricData']['dimensions'] = "string"

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'field ({}) is not of type list in the input'.format(FIELD_DIMENSIONS) in str(error.value)

    def test_parse_request_fails_when_dimensions_value_absent(self):
        event = self.create_valid_request_with_all_fields()
        del event['request']['metricData']['dimensions'][0]['value']

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'mandatory field ({}) is absent in the dimension'.format(FIELD_DIMENSION_VALUE) in str(error.value)

    def test_parse_request_succeeds_when_value_is_int(self):
        event = self.create_valid_request_with_all_fields()
        event['request']['metricData']['value'] = -1

        put_request = PutMetricRequest(event)

        assert put_request.metric_datum['Value'] == -1

    def test_parse_request_fails_when_value_is_not_number(self):
        event = self.create_valid_request_with_all_fields()
        event['request']['metricData']['value'] = 'test'

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'mandatory field ({}) is not a number'.format(FIELD_METRIC_VALUE) in str(error.value)

    def test_parse_request_fails_when_value_is_absent(self):
        event = self.create_valid_request_with_all_fields()
        del event['request']['metricData']['value']

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'mandatory field ({}) is absent in the input'.format(FIELD_METRIC_VALUE) in str(error.value)

    def test_parse_request_fails_when_unit_is_not_valid(self):
        event = self.create_valid_request_with_all_fields()
        event['request']['metricData']['unit'] = 'random_value'

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'field ({}) is not a valid value, must be in ({})'.format(FIELD_METRIC_UNIT, VALID_UNIT_VALUES) in str(
            error.value)

    def test_parse_request_fails_when_namespace_absent(self):
        event = self.create_valid_request_with_all_fields()
        del event['request']['namespace']

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'mandatory field ({}) is absent in the input'.format(FIELD_NAMESPACE) in str(error.value)

    def test_parse_request_fails_when_metricdata_absent(self):
        event = self.create_valid_request_with_all_fields()
        del event['request']['metricData']

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

    def test_parse_request_fails_when_metricdata_is_not_dict(self):
        event = self.create_valid_request_with_all_fields()
        event['request']['metricData'] = []

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'Incorrect payload format, field ({}) is not a dict'.format(FIELD_METRIC_DATA) in str(error.value)

        event['request']['metricData'] = "string"

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'Incorrect payload format, field ({}) is not a dict'.format(FIELD_METRIC_DATA) in str(error.value)

    def test_parse_request_fails_when_metricname_absent(self):
        event = self.create_valid_request_with_all_fields()
        del event['request']['metricData']['metricName']

        with pytest.raises(Exception) as error:
            PutMetricRequest(event)

        assert 'mandatory field ({}) is absent in the input'.format(FIELD_METRIC_NAME) in str(error.value)

    def test_parse_request_succeeds_when_all_optional_fields_absent(self):
        event = self.create_valid_request_with_all_fields()
        del event['request']['metricData']['dimensions']
        del event['request']['metricData']['unit']

        put_request = PutMetricRequest(event)

        assert put_request.namespace == DEFAULT_NAMESPACE
        assert put_request.metric_datum['MetricName'] == DEFAULT_METRIC_NAME
        assert put_request.metric_datum['Value'] == DEFAULT_METRIC_VALUE

    def create_valid_request_with_all_fields(self):
        return {
            "request": {
                "namespace": DEFAULT_NAMESPACE,
                "metricData": {
                    "metricName": DEFAULT_METRIC_NAME,
                    "dimensions": [
                        {
                            "name": DEFAULT_DIMENSION_NAME,
                            "value": DEFAULT_DIMENSION_VALUE
                        }
                    ],
                    "value": DEFAULT_METRIC_VALUE,
                    "unit": DEFAULT_METRIC_UNITS
                }
            }
        }
