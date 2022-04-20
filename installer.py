import os
import logging
import subprocess
import sys

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

proxy_url = os.environ.get("ALL_PROXY")
if proxy_url is not None:
    # Just try to check if proxy is http or https
    # This does not validate the full url format
    scheme = proxy_url.split(":")[0]

    if scheme == "https":
        logger.info("Creating certificate bundle with proxy root CA, and installing 'boto3', 'awsiotsdk' and 'urllib3>=1.26.7'")
        try:
            import certifi

        except ImportError:
            try:
                from pip._vendor import certifi
            except Exception:
                logger.exception(
                    "Error creating certificate bundle with proxy root CA. Python certifi module is not available on the device")
                sys.exit(1)
        try:
            with open(certifi.where(), 'r') as certify_root_ca, open(os.environ.get("GG_ROOT_CA_PATH"), 'r') as gg_root_ca, open('./ca-bundle.crt', 'w') as custom_cert_bundle:
                custom_cert_bundle.write(certify_root_ca.read())
                custom_cert_bundle.write(gg_root_ca.read())
        except Exception:
            logger.exception("Error creating certificate bundle with proxy root CA")
            sys.exit(1)
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--cert', './ca-bundle.crt', 'boto3', 'awsiotsdk', 'urllib3>=1.26.7', '--user'])
            sys.exit(0)
        except Exception:
            logger.exception(
                "Error installing dependencies. Please set 'UseInstaller' to 'False' and pre-install 'boto3', 'awsiotsdk' and 'urllib3>=1.26.7'")
            sys.exit(1)

    if scheme == "http":
        logger.info("Installing 'boto3', 'awsiotsdk' and 'urllib3>=1.26.7'")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', 'boto3', 'awsiotsdk', 'urllib3>=1.26.7', '--user'])
            sys.exit(0)
        except Exception:
            logger.exception(
                "Error installing dependencies. Please set 'UseInstaller' to 'False' and pre-install 'boto3', 'awsiotsdk' and 'urllib3>=1.26.7'")
            sys.exit(1)

logger.info("Installing 'boto3' and 'awsiotsdk'")
try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'boto3', 'awsiotsdk', '--user'])
except Exception:
    logger.exception(
        "Error installing dependencies. Please set 'UseInstaller' to 'False' and pre-install 'boto3' and 'awsiotsdk'")
    sys.exit(1)
