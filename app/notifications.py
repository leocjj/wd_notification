import pika
from time import sleep

SMS = "sms"
EMAIL = "email"
BINDING_KEYS = [SMS, EMAIL]


def callback(ch, method, properties, body):
    if method.routing_key == SMS:
        # Mock the SMS sending
        print(f"[√] SMS sent!", flush=True)
        print(f"    content: {body.decode('utf-8')}", flush=True)
    elif method.routing_key == EMAIL:
        # Mock the email sending
        print(f"[√] Email sent!", flush=True)
        print(f"    content: {body.decode('utf-8')}", flush=True)

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='news', exchange_type='topic')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    for key in BINDING_KEYS:
        channel.queue_bind(exchange='news', queue=queue_name, routing_key=key)
except Exception as e:
    print(f"Rabbitmq not ready. Need to restar this container...", flush=True)
    sleep(10)
    exit(1)

print('[*] Waiting for notifications...', flush=True)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()