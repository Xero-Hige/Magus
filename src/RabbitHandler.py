import pika


class RabbitHandler(object):
    ''' '''

    def __init__(self, queue, durable=False, host="localhost"):
        self.queue = queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=durable)

    def send_message(self, message):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   ))

    def receive_messages(self, callback):
        def _callback(ch, method, properties, message):
            callback(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(_callback,
                                   queue=self.queue)
        self.channel.start_consuming()

    def close(self):
        self.connection.close()
