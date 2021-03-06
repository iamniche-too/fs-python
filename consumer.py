#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time

from confluent_kafka import Consumer


###
### PLEASE SET THE BELOW CONFIGURATION
###

# Address of the kafka servers and topic name
# kafka_servers = '192.168.99.108:32400,192.168.99.108:32401,192.168.99.108:32402'
kafka_servers = 'internal-service-0.kafka.svc.cluster.local:32400,internal-service-1.kafka.svc.cluster.local:32401,internal-service-2.kafka.svc.cluster.local:32402'
topic_name = 'test'

# Whether to only listen for messages that occurred since the consumer started ('latest'),
# or to pick up all messages that the consumer has missed ('earliest').
# Using 'latest' means the consumer must be started before the producer.
read_topic_from = 'earliest'

# How often to indicate data rate in seconds
throughput_debug_interval_in_sec = 1

###
### Consumer code
###

kbs_in_mb = 1000

print('Connecting to Kafka @ {}'.format(kafka_servers))
c = Consumer({
    'bootstrap.servers': kafka_servers,
    'group.id': 'mygroup',
    'auto.offset.reset': read_topic_from
})

c.subscribe([topic_name])

kbs_so_far = 0

window_start_time = int(time.time())

while True:
    
    # Waits 1 second to receive a message, if it doesn't find one goes round the loop again
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue
    
    current_time = int(time.time())
            
    # Maintain figures for throughput reporting
    kbs_so_far += sys.getsizeof(msg.value())/1000
    
    # Determine if we should output a throughput figure
    window_length_sec = current_time - window_start_time
    
    if window_length_sec >= throughput_debug_interval_in_sec:
        print('Throughput in window: {} MB/s'.format(
                int(kbs_so_far / (throughput_debug_interval_in_sec*kbs_in_mb))))
        # Reset ready for the next throughput indication
        window_start_time = int(time.time())
        kbs_so_far = 0
    

c.close()
