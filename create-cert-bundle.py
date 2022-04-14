import os
import logging
import sys

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

if os.environ.get("HTTPS_PROXY") is None:
    exit()
logger.info("Creating certificate bundle with proxy root CA, to be used by pip")
try:
    import certifi

except ImportError:
    try:
        from pip._vendor import certifi
    except Exception as e:
        logger.exception("Error creating certificate bundle with proxy root CA")
        exit()
try:
    p1 = certifi.where()
    p2 = os.environ.get("GG_ROOT_CA_PATH")
    p3 = './ca-bundle.crt'
    f1 = open(p1, 'r')
    f2 = open(p2, 'r')
    f3 = open(p3, 'a+')
    f3.write(f1.read())
    f3.write(f2.read())
    f1.seek(0)
    f2.seek(0)
    f3.seek(0)
    f1.close()
    f2.close()
    f3.close()
except Exception:
    logger.exception("Error creating certificate bundle with proxy root CA")
    exit()
try:
    from pip import main as pip

    pip(['install', '--cert', './ca-bundle.crt', 'boto3', 'awsiotsdk', 'urllib3==1.26.9', '--user'])
except Exception:
    logger.exception(
        "Error installing dependencies. Please set 'UseInstaller' to 'False' and pre-install component dependencies")