import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
channel = connection.channel()
channel.exchange_declare(exchange='sms', exchange_type='topic')
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

binding_keys = ['sms', 'email']
for binding_key in binding_keys:
    channel.queue_bind(
        exchange='sms', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}:{body}")

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()