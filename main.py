
import json
from castor import CastorCore


helloWorld = json.load(open("flows/hello_world.json"))
math = json.load(open("flows/math.json"))

core = CastorCore()
flow = core.open("flows/math.json")

flow.start()

from time import sleep
sleep(2)

flow.stop()