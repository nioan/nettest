#!/usr/bin/env python3
import time
import numpy as np
import socket
from influxdb import InfluxDBClient
from scapy.all import IP, ICMP, sr1
from config import read_nettest_config


def calculate_stats(data, percentiles):
    return {
        'max': max(data) if data else None,
        'min': min(data) if data else None,
        'avg': np.mean(data) if data else None,
        'pcr': {p: np.percentile(data, p) for p in percentiles}
    }


def measure_latency(config):
    num_packets = config.get('num_packets', 50)
    timeout = config.get('timeout', 1)
    target_ip = config.get('target_ip', '8.8.8.8')
    percentiles = config.get('percentiles', [5, 95])

    sent_packets = 0
    lost_packets = 0
    latencies = []
    jitters = []
    print(f'Sending {num_packets} ICMP packets to {target_ip}')
    for _ in range(num_packets):
        # Send ICMP packet and record timestamp
        sent_time = time.time()
        response = sr1(IP(dst=target_ip) / ICMP(), timeout=timeout,
                       verbose=False)
        received_time = time.time()

        # Count packets
        sent_packets += 1
        if response is None:
            lost_packets += 1
            continue

        # Calculate latency
        latency = (received_time - sent_time) * 1000  # Convert to milliseconds
        latencies.append(latency)

        # Calculate jitter
        if len(latencies) > 1:
            jitter = abs(latency - latencies[-2])
            jitters.append(jitter)

    return {
        'sent_packets': sent_packets,
        'lost_packets': lost_packets,
        'latency_ms': calculate_stats(latencies, percentiles),
        'jitter_ms': calculate_stats(jitters, percentiles)
    }


def write_latency_to_influxdb(result, influxdb_config):
    print(f'influx_db_host: {influxdb_config.get("host", "N/A")}')
    client = InfluxDBClient(host=influxdb_config.get('host', 'localhost'),
                            port=influxdb_config.get('port', 8086),
                            username=influxdb_config.get('username', ''),
                            password=influxdb_config.get('password', ''),
                            database=influxdb_config.get(
                                'latency_database', 'latency'))
    host = socket.gethostname()
    tags = influxdb_config.get('tags', {})
    tags = {**tags, 'host': host}
    sent_packets = result['sent_packets']
    lost_packets = result['lost_packets']
    percentage_lost = (
        lost_packets / sent_packets) * 100 if sent_packets > 0 else 0

    # Prepare data points
    datapoints = [
        {
            'measurement': 'sent_packets',
            'fields': {'value': sent_packets},
            'tags': tags
        },
        {
            'measurement': 'lost_packets',
            'fields': {'value': lost_packets},
            'tags': tags
        },
        {
            'measurement': 'percentage_lost_packets',
            'fields': {'value': percentage_lost},
            'tags': tags
        }
    ]

    # Prepare latency and jitter points
    for measurement, data in [('latency_ms', result['latency_ms']), 
                              ('jitter_ms', result['jitter_ms'])]:
        for key, value in data.items():
            if key == 'pcr' and isinstance(value, dict):
                for percentile, percentile_value in value.items():
                    datapoints.append({
                        'measurement': f'{measurement}_{key}_{percentile}',
                        'fields': {'value': percentile_value},
                        'tags': tags
                    })
            else:
                datapoints.append({
                    'measurement': f'{measurement}_{key}',
                    'fields': {'value': value},
                    'tags': tags
                })
    client.write_points(datapoints)


def main():
    # Read the configuration file
    config = read_nettest_config()

    # Measure latency
    result = measure_latency(config.get('latency', {}))
    print(result)
    # Write to InfluxDB
    write_latency_to_influxdb(result, config.get('influxdb', {}))


if __name__ == '__main__':
    main()
