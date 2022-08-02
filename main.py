#!/usr/bin/env python3
""" for exec on NanoPy """
import os
import json
import time
# import requests
import asyncio
import aiohttp
from requests.auth import HTTPDigestAuth

start_time = time.time()

# url = 'http://192.168.104.154/cgi-bin/reboot.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_kernel_log.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerConfiguration.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_system_info.cgi'
# url = 'http://192.168.104.154/cgi-bin/minerStatus.cgi'
# url = 'http://192.168.104.154/cgi-bin/get_status_api.cgi'

hosts = [
    '192.168.104.158',
    '192.168.104.170',
    '192.168.104.202',
    '192.168.104.146',
    '192.168.103.214',
    '192.168.104.174',
    '192.168.104.206',
    '192.168.104.150',
    '192.168.105.106',
    '192.168.104.218',
    '192.168.104.142',
    '192.168.104.186',
    '192.168.103.194',
    '192.168.105.130',
    '192.168.104.6',
    '192.168.104.194',
    '192.168.105.94',
    '192.168.105.82',
    '192.168.105.86',
    '192.168.103.238',
    '192.168.104.190',
    '192.168.103.234',
    '192.168.105.70',
    '192.168.104.210',
    '192.168.103.226',
    '192.168.103.206',
    '192.168.104.198',
    '192.168.103.242',
    '192.168.105.98',
    '192.168.104.178',
    '192.168.103.222',
    '192.168.104.182',
    '192.168.103.198',
    '192.168.104.162',
    '192.168.105.102',
    '192.168.103.202',
    '192.168.104.154',
    '192.168.105.122',
    '192.168.103.218',
    '192.168.105.230',
    '192.168.104.166',
    '192.168.105.74',
    '192.168.105.138',
]

async def get_system_info(session: aiohttp.ClientSession, hostname: str) -> dict:
    """ Get System Info """
    url = f"http://{hostname}/cgi-bin/get_system_info.cgi"
    try:
        request = await session.get(url=url)
        try:
            json_object = json.loads(request.text)
        except json.decoder.JSONDecodeError:
            json_object = json.loads('{"minertype": "n/a"}')
    except aiohttp.ClientConnectorError:
        json_object = json.loads('{"minertype": "n/a", "Error": "connect error"}')
    return json_object

async def main() -> None:
    """ Main """
    async with aiohttp.ClientSession(auth=HTTPDigestAuth(
        os.getenv('ASIC_USERNAME'), os.getenv('ASIC_PASSWD'))) as session:
        tasks = []

        tasks = [asyncio.create_task(
            get_system_info(session, host)) for host in hosts]

        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

print(f"--- {time.time() - start_time} seconds ---")
