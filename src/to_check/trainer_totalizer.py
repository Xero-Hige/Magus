import pickle as Serializer
import random
import signal
import sys

from RabbitHandler import *

WAIT_TIME = 20
import math


def update_progress(progress):
    print ('\r[{0:100}] {1:.4f}%'.format('#' * (math.floor(progress)), progress), end='')
    return


class Status:
    def __init__(self):
        self.result = {}
        self.totals = {}
        self.coOcurrences = {}
        self.queue = RabbitHandler("features_dicts")
        self.docs = 0

    def queue_callback(self, features):
        signal.alarm(0)  # Disables alarm

        self.docs += 1

        features_dict = Serializer.loads(features)
        features_list = [x for x in features_dict]

        for i in range(len(features_list)):
            feature1 = features_list[i]
            self.totals[feature1] = self.totals.get(feature1, 0) + 1

            for j in range(i + 1, len(features_list)):
                feature2 = features_list[j]

                if (feature1, feature2) in self.coOcurrences:
                    self.coOcurrences[(feature1, feature2)] += 1
                    continue

                if (feature2, feature1) in self.coOcurrences:
                    self.coOcurrences[(feature2, feature1)] += 1
                    continue

                self.coOcurrences[(feature1, feature2)] = 1

        signal.alarm(WAIT_TIME)

    def signal_callback(self, signum, frame):
        self.queue.close()
        self.totalize()
        self.persist()
        sys.exit(0)

    def totalize(self):
        features_list = [x for x in self.totals]
        counts = self.docs

        for i in range(len(features_list)):
            feature1 = features_list[i]
            feature1_counts = self.totals[feature1]
            feature1_pmis = self.result.get(feature1, {})

            update_progress(i / len(features_list) * 100)

            for j in range(i + 1, len(features_list)):
                feature2 = features_list[j]
                feature2_counts = self.totals[feature2]
                feature2_pmis = self.result.get(feature2, {})

                coocurrence = self.coOcurrences.get((feature1, feature2), 0) + self.coOcurrences.get(
                    (feature2, feature1), 0)

                if coocurrence == 0:
                    continue

                pmi = math.log((coocurrence / counts) / ((feature1_counts / counts) * (feature2_counts / counts)))

                feature1_pmis[feature2] = pmi
                feature2_pmis[feature1] = pmi

                self.result[feature1] = feature1_pmis
                self.result[feature2] = feature2_pmis

    def persist(self):
        with open("/trainresults/dict", 'wb') as output:
            Serializer.dump(self.result, output)

        keys = list(self.result.keys())
        features = [random.choice(keys) for _ in range(10)]

        results = []

        for feature in features:
            pmis = [(v, k) for k, v in self.result[feature].items()]
            pmis.sort()
            pmis = pmis[:5] + pmis[len(pmis) - 5:]

            results.append((feature, pmis))

        with open("/trainresults/sample.txt", "wb") as output:
            for result in results:
                string = str(result[0]) + " <<-->> " + str(result[1]) + "\n"
                print(string)
                string = string.encode("utf-8")
                output.write(string)

    def start(self):
        signal.signal(signal.SIGALRM, self.signal_callback)
        self.queue.receive_messages(self.queue_callback)


def main(argv):
    totalizer = Status()
    totalizer.start()


if __name__ == '__main__':
    main(sys.argv)
