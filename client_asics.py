""" For ASICS API """
from dataclasses import dataclass
from enum import Enum
import json
from json.decoder import JSONDecodeError
from typing import TypeAlias
import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import RequestException
from exceptions import ApiServiceError
import config

Celsius: TypeAlias = float

class AsicType(str, Enum):
    ANTMINER    = 'Antminer L3+ Hiveon'
    ANTMINER_L7 = "Antminer L7"

@dataclass(slots=True, frozen=True)
class Asics:
    asic_type:   AsicType
    ipaddress:   str
    macaddr:     str
    temperature: Celsius
    hashrate: int
    voltage:  int
    fan:      int
    elapsed:  int

def get_system_info(hostname: str) -> Asics:
    status_api_response = _get_status_api_response(
        hostname=hostname
    )
    asic = _parse_status_response(status_api_response)
    return asic

def _get_status_api_response(hostname: str) -> dict:
    """ Get Miner Status """
    url = f"http://{hostname}/cgi-bin/get_system_info.cgi"
    try:
        return requests.get(url,
                               auth=HTTPDigestAuth(
                                   config.ASIC_USERNAME,
                                   config.ASIC_PASSWD),
                               timeout=5)
    except RequestException:
        raise ApiServiceError


def _parse_status_response(status_api_response: str):
    try:
        asics_dict = json.loads(status_api_response)
    except JSONDecodeError:
        raise ApiServiceError
    return Asics(
        AsicType=_parse_asic_type(asics_dict),
        ipaddress=_parse_asic_ipaddress(asics_dict),
        macaddr=_parse_asic_macaddr(asics_dict)
    )

def _parse_asic_type(asics_dict: dict) -> AsicType:
    return asics_dict["minertype"]

def _parse_asic_ipaddress(asics_dict: dict) -> str:
    return asics_dict["ipaddress"]

def _parse_asic_macaddr(asics_dict: dict) -> str:
    return asics_dict["macaddr"]

if __name__ == '__main__':
    get_system_info('192.168.103.238')
