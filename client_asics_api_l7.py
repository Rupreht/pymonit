import json
from json.decoder import JSONDecodeError
import requests
from requests.exceptions import RequestException
from requests.auth import HTTPDigestAuth

import config
from exceptions import ApiServiceError

# Only "Antminer L7"
# url = 'http://192.168.103.238/cgi-bin/summary.cgi'
# url = 'http://192.168.103.238/cgi-bin/stats.cgi'


def _get_status_api_response(hostname: str) -> dict:
    """ Get Miner Status """
    obj = {'ip': str(hostname)}
    url = f"http://{hostname}/cgi-bin/stats.cgi"
    try:
        return requests.get(url,
                               auth=HTTPDigestAuth(
                                   config.ASIC_USERNAME,
                                   config.ASIC_PASSWD),
                               timeout=5)
    except RequestException:
        raise ApiServiceError

if __name__ == '__main__':
    get_status_api('192.168.103.238')
