#!/usr/bin/env python3
""" for exec on NanoPy """
from threading import Thread, BoundedSemaphore, RLock
from ipaddress import IPv4Address, summarize_address_range
import os, sys, getopt
import json
import time
import requests
from requests.auth import HTTPDigestAuth

networs = summarize_address_range(IPv4Address('192.168.100.0'),
                                  IPv4Address('192.168.106.3'))
loker = RLock()
system_info_list = []
status_api_list = []

# url = 'http://192.168.104.154/cgi-bin/get_kernel_log.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerConfiguration.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_system_info.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerStatus.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_status_api.cgi'
# url = 'http://192.168.104.154/cgi-bin/reboot.cgi'
# Only "Antminer L7"
# url = 'http://192.168.103.238/cgi-bin/summary.cgi'
# url = 'http://192.168.103.238/cgi-bin/stats.cgi'

def get_system_info(hostname: str) -> dict:
    """ Get System Info """
    url = f"http://{hostname}/cgi-bin/get_system_info.cgi"
    obj = {}
    try:
        request = requests.get(url,
                         auth=HTTPDigestAuth(
                             os.getenv('ASIC_USERNAME'),
                             os.getenv('ASIC_PASSWD')),
                         timeout=5)
        try:
            obj = json.loads(request.text.strip())
        except json.decoder.JSONDecodeError:
            obj = {"minertype": "n/a"}
    except requests.exceptions.RequestException:
        obj = {"minertype": "n/a", "Error": "connect error"}
    loker.acquire()
    system_info_list.append(obj)
    loker.release()
    return obj

def get_status_api(hostname: str, minertype: str) -> dict:
    """ Get Miner Status """
    if minertype == 'Antminer L7':
        url = f"http://{hostname}/cgi-bin/stats.cgi"
    else:
        url =  f"http://{hostname}/cgi-bin/get_status_api.cgi"
    obj = {'ip': str(hostname)}
    try:
        request = requests.get(url,
                         auth=HTTPDigestAuth(
                             os.getenv('ASIC_USERNAME'),
                             os.getenv('ASIC_PASSWD')),
                         timeout=5)
        if minertype == 'Antminer L7':
            obj['status'] = json.loads(request.text.strip())
        else:
            obj['status'] = request.text.strip().replace("\n", "").rstrip('|').split('|')
    except requests.exceptions.RequestException:
        obj['status'] = []
    loker.acquire()
    status_api_list.append(obj)
    loker.release()
    return obj

def get_system_info_in_pool(hostname: str) -> str:
    """ Get Miner Type """
    with pool:
        get_system_info(hostname)

def get_status_api_in_pool(hostname: str, minertype: str) -> str:
    """ Get Miner Status """
    with pool:
        get_status_api(hostname, minertype)

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
        print(f'Save in data/discovery_hosts.json')

def get_status_api_all(sys_info_list: list) -> None:
    """ Get Status API All Hosts """
    if not sys_info_list:
        with open("data/discovery_hosts.json", "r", encoding="utf-8") as file:
            sys_info_list = json.load(file)

    thr_list = []
    for host in sys_info_list:
        if "n/a" in host['minertype']:
            continue
        thr = Thread(target=get_status_api_in_pool, args=(host['ipaddress'], host['minertype'],))
        thr_list.append(thr)
        thr.start()

    for i in thr_list:
        i.join()

    with open("data/status_api.json", "w", encoding="utf-8") as file:
        json.dump(status_api_list, file, indent=4, ensure_ascii=False)
        print(f'Save in data/status_api.json')

    return None

def main(argv) -> None:
    """ Main """
    try:
        options, arguments = getopt.getopt(argv, "hd",["help", "discovery"])
    except getopt.GetoptError:
        print('main.py [-d|--discovery]')
        sys.exit(2)
    for opt, arg in options:
        if opt in ('-h', '--help'):
            print('Help:\n\tmain.py [-d|--discovery]')
            sys.exit()
        if opt in ("-d", "--discovery"):
            print('Discovery Hosts: begin')
            discovery_hosts()
            print('Discovery Hosts: end')
    get_status_api_all(system_info_list)

if __name__ == '__main__':
    # Check thread's return value
    start_time = time.time()
    pool = BoundedSemaphore(value=50)
    main(sys.argv[1:])
    print(f"--- {time.time() - start_time} seconds ---")
