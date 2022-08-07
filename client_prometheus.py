""" Prometheus Client """
from client_prometheus import Counter, Gauge

asics_temp_celsius = Gauge(
    "asics_temp_celsius",
    "request temp of the host",
    ['temp', 'index', 'host'])
asics_miner_hashrate = Gauge(
    "asics_miner_hashrate",
    "request miner hashrate of the host",
    ['hr','host'])
asics_miner_voltage = Gauge(
    "asics_miner_voltage",
    "request miner voltage of the host",
    ['voltage', 'index', 'host'])
asics_miner_fan = Gauge(
    "asics_miner_fan",
    "request miner fan of the host",
    ['fan', 'index', 'host'])
asics_miner_elapsed = Counter(
    "asics_miner_elapsed",
    "request miner elapsed of the host",
    ['elapsed', 'host'])

if __name__ == '__main__':
    pass
