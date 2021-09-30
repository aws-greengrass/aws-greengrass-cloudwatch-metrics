# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

import pytest
from mock import MagicMock, patch
from src.metric.client import CloudWatchClient


@patch('botocore.credentials.CredentialResolver', autospec=True)
@patch('boto3.Session', autospec=True)
class TestCloudWatchClient(object):

    def test_successful_cw_publish(self, mock_session, mock_resolver):
        mock_cred_resolver = MagicMock()
        mock_resolver.return_value = mock_cred_resolver
        mock_cred_resolver.load_credentials.return_value = 'mock_credentials'
        mock_cw_session = MagicMock()
        mock_session.return_value = mock_cw_session
        mock_cw_client = MagicMock()
        mock_cw_session.client.return_value = mock_cw_client
        mock_cw_client.put_metric_data.return_value = 'random'

        cw_client = CloudWatchClient('us-east-1')
        put_metric_request = self.create_put_metric_request()
        response = cw_client.put_metric_data('Greengrass', put_metric_request)

        assert response == 'random'

    def test_successful_cw_publish_with_request_id(self, mock_session, mock_resolver):
        mock_cred_resolver = MagicMock()
        mock_resolver.return_value = mock_cred_resolver
        mock_cred_resolver.load_credentials.return_value = 'mock_credentials'
        mock_cw_session = MagicMock()
        mock_session.return_value = mock_cw_session
        mock_cw_client = MagicMock()
        mock_cw_session.client.return_value = mock_cw_client
        mock_cw_client.put_metric_data.return_value = {
            'ResponseMetadata': {'RequestId': 'test_id'}}

        cw_client = CloudWatchClient('us-east-1')
        put_metric_request = self.create_put_metric_request()
        response = cw_client.put_metric_data('Greengrass', put_metric_request)

        assert response == 'test_id'

    def test_failed_cw_publish(self, mock_session, mock_resolver):
        mock_cred_resolver = MagicMock()
        mock_resolver.return_value = mock_cred_resolver
        mock_cred_resolver.load_credentials.return_value = 'mock_credentials'
        mock_cw_session = MagicMock()
        mock_session.return_value = mock_cw_session
        mock_cw_client = MagicMock()
        mock_cw_session.client.return_value = mock_cw_client
        mock_cw_client.put_metric_data.side_effect = ValueError(
            'Test Exception')

        cw_client = CloudWatchClient('us-east-1')
        put_metric_request = self.create_put_metric_request()

        with pytest.raises(Exception) as error:
            response = cw_client.put_metric_data(
                'Greengrass', put_metric_request)

        assert error.match("Test Exception")

    def create_put_metric_request(self):
        return [
            {
                'MetricName': 'test_metric',
                'Dimensions': [
                    {
                        'Name': 'topic',
                        'Value': 'test_topic'
                    },
                ],
                'Timestamp': datetime(2015, 1, 1),
                'Value': 123.0,
                'Unit': 'Seconds'
            }
        ]
