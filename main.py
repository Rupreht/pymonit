#!/usr/bin/env python3
""" for exec on NanoPy """
from threading import Thread, BoundedSemaphore, RLock
from ipaddress import IPv4Address, summarize_address_range
import os
import json
import time
import requests
from requests.auth import HTTPDigestAuth

start_time = time.time()
# networs = summarize_address_range(IPv4Address('192.168.100.0'),
#                                   IPv4Address('192.168.106.3'))
networs = summarize_address_range(IPv4Address('192.168.104.127'),
                                  IPv4Address('192.168.104.255'))
loker = RLock()
system_info_list = []

# url = 'http://192.168.104.154/cgi-bin/get_kernel_log.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerConfiguration.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_system_info.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerStatus.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_status_api.cgi'
# url = 'http://192.168.104.154/cgi-bin/reboot.cgi'

def get_system_info(hostname: str) -> dict:
    """ Get System Info """
    url = f"http://{hostname}/cgi-bin/get_system_info.cgi"
    obj = {'hostname': hostname}
    try:
        request = requests.get(url,
                         auth=HTTPDigestAuth(
                             os.getenv('ASIC_USERNAME'),
                             os.getenv('ASIC_PASSWD')),
                         timeout=5)
        try:
            obj['info'] = request.text.strip()
        except json.decoder.JSONDecodeError:
            obj['info'] = {"minertype": "n/a"}
    except requests.exceptions.RequestException:
        obj['info'] = {"minertype": "n/a", "Error": "connect error"}
    loker.acquire()
    system_info_list.append(obj)
    loker.release()
    return obj

def get_system_info_in_pool(hostname: str) -> str:
    """ Get Miner Type """
    with pool:
        get_system_info(hostname)
        print(f'hostname: {hostname} is complete')

def get_addr(iterator_nets, new_prefix=30):
    """
    Get a new address on networks without network and broadcast address
    Yields:
        IPv4Address: ip addr
    """
    for net in iterator_nets:
        for subnets in net.subnets(new_prefix=new_prefix):
            for addr in subnets:
                if addr == subnets.broadcast_address:
                    continue
                if addr == subnets.network_address:
                    continue
                yield addr

def discovery_hosts():
    """ Discovery hosts """
    thr_list = []
    for addr in get_addr(networs, new_prefix=30):
        thr = Thread(target=get_system_info_in_pool, args=(addr,))
        thr_list.append(thr)
        thr.start()

    for i in thr_list:
        i.join()

    with open("data/discovery_hosts.json", "w", encoding="utf-8") as file:
        json.dump(system_info_list, file, indent=4, ensure_ascii=False)

# def main() -> None:
#     """ Main """
#     thr_list = []

#     for host in hosts:
#         thr = Thread(target=get_minertype, args=(host,))
#         thr_list.append(thr)
#         thr.start()

#     for i in thr_list:
#         i.join()

if __name__ == '__main__':
    pool = BoundedSemaphore(value=25)
    discovery_hosts()
    # Check thread's return value
    # main()
    print(f"--- {time.time() - start_time} seconds ---")
