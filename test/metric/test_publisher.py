# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

from mock import patch, MagicMock
import time

def create_default_metric_datum():
    return {
        'MetricName' : 'test_metric',
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

class TestMetricPublisherWithBatchDisabled(object):

    def setup_method(self, method):
        self.mock_iot_class = patch('awsiot.greengrasscoreipc.connect', autospec=True).start()
        self.mock_iot = MagicMock()
        self.mock_iot_class.return_value = self.mock_iot
        self.mock_cw_class = patch('src.metric.client.CloudWatchClient', autospec=True).start()
        self.mock_cw = MagicMock()
        self.mock_cw.put_metric_data.return_value = {}
        self.mock_cw_class.return_value = self.mock_cw


    def teardown_method(self, method):
        patch.stopall()

    def test_add_metric(self):
        import src.metric.publisher as publisher
        metric_datum = create_default_metric_datum()
        metric_publisher = publisher.MetricPublisher('GG', 'us-east-1', 0)
        self.mock_cw.reset_mock()
        i = 0
        while i < publisher.METRIC_BATCH_SIZE - 1:
            metric_publisher.add_metric(metric_datum)
            self.mock_cw.put_metric_data.assert_called_with('GG', [metric_datum])
            i = i + 1

        assert metric_publisher.get_size() == 0

    def test_replace_metric(self):
        import src.metric.publisher as publisher
        metric_datum = create_default_metric_datum()
        metric_publisher = publisher.MetricPublisher('GG', 'us-east-1', 0)
        self.mock_cw.reset_mock()
        # This wont add metrics because the size if full
        i = 0
        while i < publisher.METRIC_BATCH_SIZE - 1:
            metric_publisher.replace_metric(metric_datum)
            self.mock_cw.put_metric_data.assert_not_called()
            i = i + 1

        assert metric_publisher.get_size() == 0