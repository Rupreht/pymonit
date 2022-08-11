""" Get Status """
from dataclasses import dataclass
import json
from typing import TypeAlias
import requests
from requests.auth import HTTPDigestAuth
import config

# url = 'http://192.168.104.154/cgi-bin/get_kernel_log.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerConfiguration.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_system_info.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerStatus.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_status_api.cgi'
# url = 'http://192.168.104.154/cgi-bin/reboot.cgi'

Celsius: TypeAlias = float

@dataclass(slots=True, frozen=True)
class AsicStatus:
    """ Obj AsicStatus """
    temperature: Celsius
    hashrate: dict
    voltage:  int
    fan:      list
    elapsed:  int


def get_status_api(hostname: str) -> dict:
    """ Get Miner Status """
    obj = {'ip': str(hostname)}
    url =  f"http://{hostname}/cgi-bin/get_status_api.cgi"
    try:
        request = requests.get(url,
                               auth=HTTPDigestAuth(
                                   config.ASIC_USERNAME,
                                   config.ASIC_PASSWD),
                               timeout=5)
        obj['status'] = request.text.strip().replace("\n", "").rstrip('|').split('|')
    except requests.exceptions.RequestException:
        obj['status'] = []
    return obj

if __name__ == '__main__':
    """ Test """
    # normal
    print(get_status_api('192.168.104.154'))
    # empty
    print(get_status_api('192.168.104.153'))
