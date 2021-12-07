from kafka import KafkaConsumer
import json
import sys
import os
import time


CONFIG_KAFKA_GROUP_ID = sys.argv[1] if len(sys.argv) > 1 else "default002"
CONFIG_KAFKA_TOPIC = os.getenv('CONFIG_KAFKA_TOPIC','DEFAULT')
CONFIG_KAFKA_SERVERS = os.getenv('CONFIG_KAFKA_SERVERS','').split(',')
CONFIG_KAFKA_OFFSET_RESET = os.getenv('CONFIG_KAFKA_OFFSET_RESET','latest')
CONFIG_KAFKA_AUTO_COMMIT = os.getenv("CONFIG_KAFKA_AUTO_COMMIT", 'false').lower() in ('true',)
CONFIG_KAFKA_INTERVAL_COMMIT = int(os.getenv('CONFIG_KAFKA_INTERVAL_COMMIT',5000))


while True:
    try:
        consumer = KafkaConsumer(
            CONFIG_KAFKA_TOPIC,
            group_id=CONFIG_KAFKA_GROUP_ID,
            bootstrap_servers=CONFIG_KAFKA_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('ascii')),
            auto_offset_reset=CONFIG_KAFKA_OFFSET_RESET,
            enable_auto_commit=CONFIG_KAFKA_AUTO_COMMIT,
            auto_commit_interval_ms=CONFIG_KAFKA_INTERVAL_COMMIT
        )

        print(f"Start consumer GROUP_ID: {CONFIG_KAFKA_GROUP_ID}")


        for message in consumer:
            print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                message.offset, message.key,
                                                message.value))
    except Exception as error:
        print(error)
        time.sleep(5)