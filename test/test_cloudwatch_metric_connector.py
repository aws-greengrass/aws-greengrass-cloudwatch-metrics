# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

import importlib
from mock import patch, MagicMock

DEFAULT_NAMESPACE = 'Greengrass'
DEFAULT_METRIC_NAME = 'Count'
DEFAULT_METRIC_VALUE = 12.0
DEFAULT_METRIC_UNITS = 'Seconds'
DEFAULT_DIMENSION_NAME = 'hostname'
DEFAULT_DIMENSION_VALUE = 'test_hostname'

def get_sample_config():
    return {
        'PublishRegion' : 'eu-west-2',
        'PublishInterval' : '5',
        'MaxMetricsToRetain' : '5000',
        'InputTopic' : 'sample/put',
        'OutputTopic' : 'sample/status',
        'PubSubToIoTCore' : 'False'
    }

def create_valid_request_with_all_fields():
    return  {
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

class TestHandler(object):

    def setup_method(self, method):
        self.mock_iot_class = patch('awsiot.greengrasscoreipc.connect', autospec=True).start()
        self.mock_iot = MagicMock()
        self.mock_iot_class.return_value = self.mock_iot
        self.mock_metric_manager_class = patch('src.metric.manager.MetricsManager', autospec=True).start()
        self.mock_manager = MagicMock()
        self.mock_manager.add_metric.return_value = True
        self.mock_metric_manager_class.return_value = self.mock_manager
        self.mock_ipc_class = patch('src.ipc_utils.IPCUtils', autospec=True).start()
        self.mock_ipc = MagicMock()
        self.mock_ipc.subscribe_to_pubsub_topic.return_value = True
        self.mock_ipc.subscribe_to_iot_topic.return_value = True
        self.mock_ipc_class.return_value = self.mock_ipc
        print("setup done")


    def teardown_method(self, method):
        patch.stopall()

 
    def test_parsing_config_parameters(self):
        sample_config = get_sample_config()
        self.mock_ipc.get_configuration.return_value = sample_config

        import src.cloudwatch_metric_connector as app
        importlib.reload(app)
        
        assert app.PUBLISH_REGION == sample_config['PublishRegion']
        assert app.PUBLISH_INTERVAL_SEC == int(sample_config['PublishInterval'])
        assert app.MAX_METRICS == int(sample_config['MaxMetricsToRetain'])
        assert app.INPUT_TOPIC == sample_config['InputTopic']
        assert app.OUTPUT_TOPIC == sample_config['OutputTopic']
        assert app.PUBSUB_TO_IOT_CORE == sample_config['PubSubToIoTCore']
        assert app.pubsub_to_iot_core == False

    def test_invalid_config_parameters(self):
        invalid_config = get_sample_config()
        invalid_config['PublishInterval'] = 1000
        invalid_config['MaxMetricsToRetain'] = 1000
        self.mock_ipc.get_configuration.return_value = invalid_config

        valid_config = get_sample_config()
        valid_config['PublishInterval'] = 900
        valid_config['MaxMetricsToRetain'] = 2000
        
        import src.cloudwatch_metric_connector as app
        importlib.reload(app)

        assert app.PUBLISH_INTERVAL_SEC == valid_config['PublishInterval']
        assert app.MAX_METRICS == valid_config['MaxMetricsToRetain']