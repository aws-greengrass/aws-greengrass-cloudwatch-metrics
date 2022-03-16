# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import os

import boto3
from botocore import credentials, exceptions, config
from botocore.session import get_session
from src import utils

logger = utils.logger
gg_root_ca_path = os.getenv("GG_ROOT_CA_PATH")


class CloudWatchClient:
    def __init__(self, region):
        # Only look for Credentials from ContainerProvider
        container_creds_resolver = credentials.CredentialResolver([credentials.ContainerProvider()])
        container_creds = container_creds_resolver.load_credentials()
        session = get_session()
        if container_creds is not None:
            session._credentials = container_creds
            self.client = boto3.Session(botocore_session=session).client(
                'cloudwatch', region, config=config.Config(proxies_config={'proxy_ca_bundle': gg_root_ca_path}))
        else:
            raise exceptions.CredentialRetrievalError(
                provider=credentials.ContainerProvider.METHOD,
                error_msg="Container credentials were not found"
            )

    def put_metric_data(self, namespace, metric_data):
        put_metric_args = {'Namespace': namespace, 'MetricData': metric_data}
        try:
            response = self.client.put_metric_data(**put_metric_args)
            logger.info(
                "Cloudwatch metrics published successfully with response: %s", response)
            if type(response) is dict and response.get('ResponseMetadata'):
                if type(response['ResponseMetadata']) is dict and response['ResponseMetadata'].get('RequestId'):
                    return response['ResponseMetadata']['RequestId']
            # if there is no request id, just send back whole response
            return response
        except Exception:
            logging.exception("Error was encountered publishing to cloudwatch: ")
            raise
