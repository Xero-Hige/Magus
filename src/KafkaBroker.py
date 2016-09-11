from pykafka import KafkaClient
import pickle

HOSTS = '192.168.99.100:9092'


class __KafkaBroker(object):
    def __init__(self, topic):
        self.topic = topic
        self.client = KafkaClient(hosts=HOSTS)
        self.kafka_topic = self.client.topics[topic]


class KafkaReader(__KafkaBroker):
    def __init__(self, topic):
        super().__init__(topic)
        self.consumer = self.kafka_topic.get_simple_consumer()


    def read(self):

        for data in self.consumer:  # FIXME
            if data:
                return pickle.loads(data.value)


class KafkaWriter(__KafkaBroker):
    def __init__(self, topic):
        super().__init__(topic)
        self.producer = self.kafka_topic.get_sync_producer()

    def write(self, object):
        data = pickle.dumps(object)
        self.producer.produce(data)
