# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from functools import reduce

from src import utils
from src.metric import publisher

logger = utils.logger


class MetricsManager:
    ''' This class stores all metrics in memory. metrics are keyed by namespace. Each namespace points 
    to a list of metric objects
    arguments:
    region -- Cloudwatch region to upload metrics to
    put_metric_interval -- time period (s) between two successive put metric calls to cloudwatch
    max_bucket_size -- total number of metrics present in memory. This includes total metric objects
            across all namespaces

    This class is responsible for managing the metric_bucket whose upper bound is an input.
    metrics are paritioned by namespaces, which means that all bucket operations are specific 
    to namespaces. This also implies that if metric bucket is full and a metric with a new 
    namespace is added, it will be rejected. If a metric with existing namespace is added, it
    replaces the oldest entry in its namespace.
    '''

    def __init__(self, region, put_metric_interval, max_bucket_size):
        self.metrics_bucket = {}
        self.__region = region
        self.__put_metric_interval = put_metric_interval
        self.__max_bucket_size = max_bucket_size

    def __create_new_metric(self, namespace):
        self.metrics_bucket[namespace] = publisher.MetricPublisher(
            namespace, self.__region, self.__put_metric_interval)

    def add_metric(self, namespace, metric_datum):
        if self.metrics_bucket.get(namespace) is None:
            self.__create_new_metric(namespace)

        metric_publisher = self.metrics_bucket[namespace]
        metric_publisher.replace_metric(
            metric_datum) if self.__get_metrics_bucket_size() > self.__max_bucket_size else metric_publisher.add_metric(
            metric_datum)

    def __get_metrics_bucket_size(self):
        if not self.metrics_bucket.values():
            return 0

        return reduce((lambda x, y: x + y.get_size()), self.metrics_bucket.values(), 0)
