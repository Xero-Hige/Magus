import random
import time

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-1d2d27fc-12bd-11e8-91c1-eac6831c625c"
pnconfig.publish_key = "pub-c-7a828306-4ddf-425c-80ec-1e4f8763c088"
pnconfig.ssl = False

pubnub = PubNub(pnconfig)

pubnub.subscribe().channels('happy').execute()

while True:
    from pubnub.exceptions import PubNubException

    try:
        envelope = pubnub.publish().channel("happy").message({
            "status": True,
            'lat':    random.choice([-124, -123, -122, -121, -120]) + random.random(),
            'long':   random.choice([35, 36, 37, 38, 39]) + random.random()
        }).sync()
        print("publish timetoken: %d" % envelope.result.timetoken)
    except PubNubException as e:
        print("Error")

    time.sleep(0.2)
