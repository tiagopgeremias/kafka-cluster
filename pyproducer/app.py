from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from datetime import datetime
from random import randint
import time
import os

CONFIG_KAFKA_TOPIC = os.getenv('CONFIG_KAFKA_TOPIC','DEFAULT')
CONFIG_KAFKA_SERVERS = os.getenv('CONFIG_KAFKA_SERVERS','').split(',')
CONFIG_KAFKA_SEND_TIMEOUT = int(os.getenv('CONFIG_KAFKA_SEND_TIMEOUT',10))
CONFIG_KAFKA_ACKS = os.getenv('CONFIG_KAFKA_ACKS','all')
CONFIG_KAFKA_RETRIES_CONNECT = int(os.getenv('CONFIG_KAFKA_RETRIES_CONNECT',3))


while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers=CONFIG_KAFKA_SERVERS, 
            acks=CONFIG_KAFKA_ACKS,
            retries=CONFIG_KAFKA_RETRIES_CONNECT
        )

        def newOrder():
            subtotal = 0
            order = {
                "id": randint(10000,99999),
                "date": str(datetime.now()),
                "client_id": randint(10000,99999),
                "items": [],
                "subtotal": 0,
                "discount": 0,
                "total": 0
            }
            
            for _ in range(randint(1,10)):
                order['items'].append({
                    "id": randint(10000,99999),
                    "qtd": randint(1,10),
                    "price": randint(100,1000)
                })

            for item in order["items"]:
                subtotal =  subtotal + (item['qtd'] * item['price'])
                
            discount = randint(0,int(subtotal/2))
            
            order["subtotal"] = subtotal
            order["discount"] = discount
            order["total"] = subtotal - discount
            
            return order

        while True:
            for i in range(randint(5,100)):
                pedido = newOrder()
                print(f'Processando... [{i+1}]')
                ksend = producer.send(CONFIG_KAFKA_TOPIC, value=json.dumps(pedido, ensure_ascii=False).encode('gbk') )
                try:
                    record_metadata = ksend.get(timeout=CONFIG_KAFKA_SEND_TIMEOUT)
                except KafkaError as error:
                    print(error)
                    pass
            time.sleep(randint(2,10))
    except Exception as error:
        print(error)
        time.sleep(5)    
