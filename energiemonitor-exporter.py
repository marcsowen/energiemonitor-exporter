#!/usr/bin/python3 -u

import json
import time

import requests
from prometheus_client import start_http_server, Gauge

autarky = Gauge('autarky', "Autoarky of region", ['region_code'])
energy_mix = Gauge('energy_mix', 'Energy mix of region', ['region_code'])
num_installations = Gauge('num_installations', 'Number of installations', ['region_code', 'type', 'name'])
usage = Gauge('usage', 'Current amount per time period in kWh', ['region_code', 'type', 'name'])
installed_capacity = Gauge('installed_capacity', 'Total installed capacity', ['region_code', 'type', 'name'])

if __name__ == '__main__':
    print("EnergieMonitor exporter v0.2\n")
    region_codes = ['03355', '03355022']
    server_port = 3325

    print("Region codes: " + str(region_codes) + "\n")
    print("Port        : " + str(server_port) + "\n")

    start_http_server(server_port)
    while True:
        for rg_id in region_codes:
            response = json.loads(requests.get('https://api-energiemonitor.eon.com/meter-data?regionCode=' + rg_id)
                                  .content.decode('UTF-8'))

            autarky.labels(region_code=rg_id).set(response['autarky'])
            energy_mix.labels(region_code=rg_id).set(response['energyMix'])

            for consumption in response['consumptions']['list']:
                name = consumption['name']
                if consumption['numberOfInstallations']:
                    num_installations.labels(region_code=rg_id, type='consumption', name=name).set(
                        consumption['numberOfInstallations'])
                if consumption['usage']:
                    usage.labels(region_code=rg_id, type='consumption', name=name).set(consumption['usage'])

            for feed_in in response['feedIn']['list']:
                name = feed_in['name']
                if feed_in['numberOfInstallations']:
                    num_installations.labels(region_code=rg_id, type='feed_in', name=name).set(
                        feed_in['numberOfInstallations'])
                if feed_in['usage']:
                    usage.labels(region_code=rg_id, type='feed_in', name=name).set(feed_in['usage'])
                if feed_in['installedCapacity']:
                    installed_capacity.labels(region_code=rg_id, type='feed_in', name=name).set(
                        feed_in['installedCapacity'])

        time.sleep(300)
