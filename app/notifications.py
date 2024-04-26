import pika
from time import sleep

SMS = "sms"
EMAIL = "email"
BINDING_KEYS = [SMS, EMAIL]


def callback(ch, method, properties, body):
    if method.routing_key == SMS:
        # Mock the SMS sending
        body = body.decode('utf-8').replace("[", "").replace("]", "").replace("'", "")
        body = body.replace("\\n", "\n").split(", ")
        phone = body.pop()
        print(f"[√] SMS sent to: {phone}", flush=True)
        message = " ".join(body)
        print(f"    content: {message}", flush=True)
    elif method.routing_key == EMAIL:
        # Mock the email sending
        body = body.decode('utf-8').replace("[", "").replace("]", "").replace("'", "")
        body = body.replace("\\n", "\n").split(", ")
        email = body.pop()
        print(f"[√] Email sent to: {email}", flush=True)
        message = " ".join(body)
        print(f"    content: {message}", flush=True)

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