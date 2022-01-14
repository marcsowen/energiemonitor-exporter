#!/usr/bin/python3 -u

import json
import time

import requests
from prometheus_client import start_http_server, Gauge

num_installations = Gauge('num_installations', 'Number of installations', ['type', 'name'])
usage = Gauge('usage', 'Current amount per time period in kWh', ['type', 'name'])
installed_capacity = Gauge('installed_capacity', 'Total installed capacity', ['type', 'name'])

if __name__ == '__main__':
    print("EnergieMonitor exporter v0.1\n")
    region_code = '03355'
    server_port = 3325

    print("Region code: " + str(region_code) + "\n")
    print("Port       : " + str(server_port) + "\n")

    start_http_server(server_port)
    while True:
        response = json.loads(requests.get('https://api-energiemonitor.eon.com/meter-data?regionCode=' + region_code)
                              .content.decode('UTF-8'))

        for consumption in response['consumptions']['list']:
            name = consumption['name']
            num_installations.labels(type='consumption', name=name).set(consumption['numberOfInstallations'])
            usage.labels(type='consumption', name=name).set(consumption['usage'])

        for feed_in in response['feedIn']['list']:
            name = feed_in['name']
            num_installations.labels(type='feed_in', name=name).set(feed_in['numberOfInstallations'])
            usage.labels(type='feed_in', name=name).set(feed_in['usage'])
            installed_capacity.labels(type='feed_in', name=name).set(feed_in['installedCapacity'])

        time.sleep(300)
