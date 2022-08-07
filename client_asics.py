""" For ASICS API AsicSystemInfo """
from dataclasses import dataclass
from enum import Enum
import json
from json.decoder import JSONDecodeError
from typing import TypeAlias
import urllib.request
from urllib.error import URLError

import config
from exceptions import ApiServiceError


Ipaddress: TypeAlias = str
Macaddr:   TypeAlias = str

class AsicType(str, Enum):
    """ Enum ASIC Types """
    ANTMINER    = 'Antminer L3+ Hiveon'
    ANTMINER_L7 = "Antminer L7"


@dataclass(slots=True, frozen=True)
class AsicSystemInfo:
    """ Obj Asic """
    asictype:    AsicType
    ipaddress:   Ipaddress
    macaddr:     Macaddr


def get_system_info(hostname: str) -> AsicSystemInfo:
    """ Get Systen Info """
    status_api_response = _get_status_api_response(
        hostname=hostname
    )
    asic = _parse_status_response(status_api_response)
    return asic

def _get_status_api_response(hostname: str) -> dict:
    """ Get Miner Status """
    url = f"http://{hostname}/cgi-bin/get_system_info.cgi"
    try:
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, config.ASIC_USERNAME,
                                  config.ASIC_PASSWD)
        auth_handler = urllib.request.HTTPDigestAuthHandler(password_mgr)
        opener = urllib.request.build_opener(auth_handler)
        urllib.request.install_opener(opener)
        return urllib.request.urlopen(url).read()
    except URLError:
        raise ApiServiceError

# def _get_status_api_response(hostname: str) -> dict:
#     print(f'Get {hostname}')
#     with open("tmp/get_system_info_l7.json", "r", encoding="utf-8") as file:
#         return file.read()

def _parse_status_response(status_api_response: str):
    try:
        asics_dict = json.loads(status_api_response)
    except JSONDecodeError:
        raise ApiServiceError
    return AsicSystemInfo(
        asictype=_parse_asic_type(asics_dict),
        ipaddress=_parse_asic_ipaddress(asics_dict),
        macaddr=_parse_asic_macaddr(asics_dict)
    )

def _parse_asic_type(asics_dict: dict) -> AsicType:
    try:
        asic_type_str = str(asics_dict["minertype"])
    except (IndexError, KeyError):
        raise ApiServiceError
    asic_types = {
        'Antminer L3+ Hiveon': AsicType.ANTMINER,
        'Antminer L7': AsicType.ANTMINER_L7
    }
    for _str, _asic_type in asic_types.items():
        if asic_type_str.startswith(_str):
            return _asic_type
    raise ApiServiceError

def _parse_asic_ipaddress(asics_dict: dict) -> Ipaddress:
    return asics_dict["ipaddress"]

def _parse_asic_macaddr(asics_dict: dict) -> Macaddr:
    return asics_dict["macaddr"]

if __name__ == '__main__':
    """ Test """
    print(get_system_info('192.168.103.238'))
    print(get_system_info('192.168.104.158'))
