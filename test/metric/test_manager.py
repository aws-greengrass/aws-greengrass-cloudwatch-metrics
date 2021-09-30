# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import time

from mock import MagicMock, patch


class TestMetricManager(object):

    def setup_method(self, method):
        self.mock_iot_class = patch(
            'awsiot.greengrasscoreipc.connect', autospec=True).start()
        self.mock_iot = MagicMock()
        self.mock_iot_class.return_value = self.mock_iot
        self.mock_publisher_class = patch(
            'src.metric.publisher.MetricPublisher', autospec=True).start()
        self.mock_publisher = MagicMock()
        self.mock_publisher_class.return_value = self.mock_publisher

    def teardown_method(self, method):
        patch.stopall()

    def test_add_metric(self):
        from src.metric.manager import MetricsManager

        # always return size for bucket as 0 so that we keep on adding metrics
        self.mock_publisher.get_size.return_value = 0
        metric_datum = self.create_default_metric_datum()
        metric_manager = MetricsManager('us-east-1', 5, 100)

        metric_manager.add_metric('GG', metric_datum)
        self.mock_publisher.add_metric.assert_called_with(metric_datum)
        assert len(metric_manager.metrics_bucket.keys()) == 1

        metric_manager.add_metric('GG1', metric_datum)
        self.mock_publisher.add_metric.assert_called_with(metric_datum)
        assert len(metric_manager.metrics_bucket.keys()) == 2

        metric_manager.add_metric('GG2', metric_datum)
        self.mock_publisher.add_metric.assert_called_with(metric_datum)
        assert len(metric_manager.metrics_bucket.keys()) == 3

        # assert that metric added to same namespace goes to same bucket
        metric_manager.add_metric('GG2', metric_datum)
        self.mock_publisher.add_metric.assert_called_with(metric_datum)
        assert len(metric_manager.metrics_bucket.keys()) == 3

    def test_replace_metric_with_only_one_namespace(self):
        from src.metric.manager import MetricsManager
        metric_datum = self.create_default_metric_datum()
        metric_manager = MetricsManager('us-east-1', 5, 3)

        # return 2 as the size of each namespace metrics
        self.mock_publisher.get_size.return_value = 2

        # now an add should trigger add_metric()
        metric_manager.add_metric('GG', metric_datum)
        self.mock_publisher.add_metric.assert_called_once_with(metric_datum)

        # return 2 as the size of each namespace metrics
        self.mock_publisher.get_size.return_value = 4

        # now an add should trigger replace_metric()
        metric_manager.add_metric('GG', metric_datum)
        self.mock_publisher.replace_metric.assert_called_once_with(
            metric_datum)

    def test_replace_metric_with_multiple_namespaces(self):
        from src.metric.manager import MetricsManager
        metric_datum = self.create_default_metric_datum()
        metric_manager = MetricsManager('us-east-1', 5, 2)

        # return 0 as the size of each namespace metrics
        self.mock_publisher.get_size.return_value = 0

        # now an add should trigger add_metric()
        metric_manager.add_metric('GG', metric_datum)
        metric_manager.add_metric('GG1', metric_datum)
        metric_manager.add_metric('GG2', metric_datum)

        # return 1 as the size of each namespace metrics
        # this would return total size of bucket as 3
        # and should trigger replace for a new metric as our max_size is 2
        self.mock_publisher.get_size.return_value = 1

        metric_manager.add_metric('GG', metric_datum)
        self.mock_publisher.replace_metric.assert_called_with(metric_datum)

        metric_manager.add_metric('GG1', metric_datum)
        self.mock_publisher.replace_metric.assert_called_with(metric_datum)

        metric_manager.add_metric('GG2', metric_datum)
        self.mock_publisher.replace_metric.assert_called_with(metric_datum)

        metric_manager.add_metric('GG2', metric_datum)
        self.mock_publisher.replace_metric.assert_called_with(metric_datum)

        # a new namespace should also trigger a replace
        metric_manager.add_metric('GG3', metric_datum)
        self.mock_publisher.replace_metric.assert_called_with(metric_datum)

    def create_default_metric_datum(self):
        return {
            'MetricName': 'test_metric',
            'Dimensions': [
                {
                    'Name': 'topic',
                    'Value': 'test_topic'
                },
            ],
            'Timestamp': time.time(),
            'Value': 123.0,
            'Unit': 'Seconds'
        }
