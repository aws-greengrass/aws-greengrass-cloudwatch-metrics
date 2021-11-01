# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import queue as Queue
from threading import Thread, Timer

from botocore.exceptions import ConnectionError
from src import ipc_utils, utils
from src.metric import client as CloudWatch

RESPONSE_FIELD_CW_ID = 'cloudwatch_rid'
RESPONSE_FILED_NAMESPACE = 'namespace'
ipc = ipc_utils.IPCUtils()


METRIC_BATCH_SIZE = 20
# This is derived from 150 TPS limit of CW, since there are potentially 2 threads dequeing
# one is the periodic flush and other synchronous add_metric call
# any value < 150/2 should be ok here.
DEFAULT_MAX_BATCHES_TO_UPLOAD = 50
# If we have a lot of backup to flush, mostly we are having connectivity issues
# which are going to persist, if customer is sending lot of metrics,
# we would dial down the rate of upload, this is only applicable to sync uploads
# background thread would keep on trying to drain at max speed
MAX_QUEUE_SIZE_FOR_DIAL_DOWN_MODE = DEFAULT_MAX_BATCHES_TO_UPLOAD * METRIC_BATCH_SIZE
MAX_BATCHES_TO_UPLOAD_IN_DIAL_DOWN_MODE = 10

logger = utils.logging.getLogger()


class MetricPublisher:
    def __init__(self, namespace, region, put_metric_interval):
        self.__namespace = namespace
        self.__metric_list = Queue.PriorityQueue(0)
        self.__cw_client = CloudWatch.CloudWatchClient(region)
        self.__put_metric_interval = put_metric_interval
        self.__start_flush_timer()
        self.__counter = 0

    def get_size(self):
        return self.__metric_list.qsize()

    def replace_metric(self, metric_datum):
        try:
            self.__metric_list.get_nowait()
            self.add_metric(metric_datum)
        except Queue.Empty as e:
            # queue is empty, nothing to replace
            pass

    def add_metric(self, metric_datum):
        self.__put_metric_in_queue(metric_datum)

        if self.__metric_list.qsize() >= METRIC_BATCH_SIZE or self.__put_metric_interval == 0:
            # This is a safety check for not blowing up CW when we have thousands
            # of metrics in buffer to get flushed.
            # Since this is a sync call, customer RPS can derive number of calls to CW
            # keep this limited so that, background thread does all the work
            max_batches_to_upload = DEFAULT_MAX_BATCHES_TO_UPLOAD
            if self.__metric_list.qsize() > MAX_QUEUE_SIZE_FOR_DIAL_DOWN_MODE:
                max_batches_to_upload = MAX_BATCHES_TO_UPLOAD_IN_DIAL_DOWN_MODE

            self.flush_metrics(max_batches_to_upload)

    def __start_flush_timer(self):
        if self.__put_metric_interval > 0:
            self.timer = Timer(self.__put_metric_interval,
                               self.__start_timer_and_flush_metrics)
            self.timer.start()

    def __put_metric_in_queue(self, metric_datum):
        # Re-initialize the metric ordering if the queue is empty after the previous flush metrics call
        if self.__metric_list.qsize() == 0:
            self.__counter = 0
        self.__counter += 1
        self.__metric_list.put_nowait(
            (metric_datum['Timestamp'], self.__counter, metric_datum))

    def __put_metric_batch_in_queue(self, metric_batch):
        for metric in metric_batch:
            self.__put_metric_in_queue(metric)

    def __get_metric_batch(self):
        batch = []
        for _ in range(METRIC_BATCH_SIZE):
            try:
                _, _, metric = self.__metric_list.get_nowait()
                batch.append(metric)
            except Queue.Empty as e:
                break

        return batch

    def __start_timer_and_flush_metrics(self, batches_to_upload=DEFAULT_MAX_BATCHES_TO_UPLOAD):
        self.__start_flush_timer()
        self.flush_metrics(batches_to_upload)

    '''
    This method runs in a separate thread and dequeues metrics.
    It may happen that qsize gets changed (only incremented) while this thread is 
    running, which means it will only dequeue lesser items than
    new qsize. It also might happen that some metrics are replaced
    by the time this method runs again. We should be fine in 
    both the cases as we dont guarantee ordering in general.
    '''

    def flush_metrics(self, batches_to_upload):
        from src.cloudwatch_metric_connector import (OUTPUT_TOPIC,
                                                     pubsub_to_iot_core)
        num_metrics = self.__metric_list.qsize()
        if num_metrics == 0:
            return

        num_metrics_tried = 0
        total_batches_tried = 0
        while num_metrics_tried < num_metrics and total_batches_tried < batches_to_upload:
            # Grab a batch of max METRIC_BATCH_SIZE metrics
            batch = self.__get_metric_batch()
            if batch:
                response = {}
                try:
                    cw_response = self.__cw_client.put_metric_data(
                        self.__namespace, batch)
                    response_payload = {RESPONSE_FIELD_CW_ID: cw_response,
                                        RESPONSE_FILED_NAMESPACE: self.__namespace}
                    response = utils.generate_success_response(
                        "", **response_payload)
                except ConnectionError as e:  # add throttled errors
                    self.__put_metric_batch_in_queue(batch)
                except Exception as e:
                    response = utils.generate_error_response("", str(e.__class__), str(
                        e), **{RESPONSE_FILED_NAMESPACE: self.__namespace})
                finally:
                    if response:
                        Thread(
                            target=ipc.publish_message,
                            args=(OUTPUT_TOPIC, response, pubsub_to_iot_core),
                        ).start()

            # its fine if last batch has < METRIC_BATCH_SIZE,
            # num_metrics_tried should be greater than num_metrics to break the loop
            # thats all that matters
            num_metrics_tried = num_metrics_tried + METRIC_BATCH_SIZE
            total_batches_tried = total_batches_tried + 1
