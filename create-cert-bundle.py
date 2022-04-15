import os
import logging
import sys

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

proxy_url = os.environ.get("ALL_PROXY")
if proxy_url is None:
    # No proxy configured
    sys.exit(0)

# Just try to check if proxy scheme is http or https
# This does not validate the full url format
scheme = proxy_url.split(":")[0]
if scheme != "https":
    # Not https proxy
    sys.exit(0)

logger.info("Creating certificate bundle with proxy root CA, and installing dependencies")
try:
    import certifi

except ImportError:
    try:
        from pip._vendor import certifi
    except Exception as e:
        logger.exception("Error creating certificate bundle with proxy root CA")
        sys.exit(1)

p1 = certifi.where()
p2 = os.environ.get("GG_ROOT_CA_PATH")
p3 = './ca-bundle.crt'
try:
    with open(p1, 'r') as f1, open(p2, 'r') as f2, open(p3, 'w') as f3:
        f3.write(f1.read())
        f3.write(f2.read())
except Exception:
    logger.exception("Error creating certificate bundle with proxy root CA")
    sys.exit(1)
try:
    from pip import main as pip

    pip(['install', '--cert', './ca-bundle.crt', 'boto3', 'awsiotsdk', 'urllib3==1.26.9', '--user'])
except Exception:
    logger.exception(
        "Error installing dependencies. Please set 'UseInstaller' to 'False' and pre-install component dependencies")
    sys.exit(1)
