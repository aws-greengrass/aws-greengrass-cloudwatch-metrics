## AWS Greengrass Cloudwatch Metrics

This is an AWS GreengrassV2 Component (`aws.greengrass.Cloudwatch`) that publishes custom metrics from Greengrass core devices to Amazon CloudWatch.
The component enables components to publish CloudWatch metrics, which you can use to monitor and analyze the Greengrass core device's environment.
To publish a CloudWatch metric with this component, publish a message to a topic where this component subscribes.
By default, this component subscribes to the `cloudwatch/metric/put` and publishes status response to the `cloudwatch/metric/put/status` local publish/subscribe topic.
You can specify other topics, including AWS IoT Core MQTT topics, when you deploy this component.

## Sample Configuration

```$xslt
{
  "PublishRegion": us-east-1,
  "PublishInterval": 20,
  "MaxMetricsToRetain": 5000,
  "InputTopic": "cloudwatch/metric/put",
  "OutputTopic": "cloudwatch/metric/put/status",
  "PubSubToIoTCore": false,
  "LogLevel": "INFO",
  "UseInstaller": true
}
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

