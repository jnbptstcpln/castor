
import time
from castor import Daemon


daemon = Daemon()
daemon.start()
time.sleep(5)
daemon.stop()
print(daemon.logs)