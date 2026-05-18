from furhat_realtime_api import FurhatClient
import logging
import time

furhat = FurhatClient("127.0.0.1")  # Add authentication key as second argument if needed
furhat.set_logging_level(logging.INFO)  # Use logging.DEBUG for more details
furhat.connect()

furhat.request_speak_text("Hello world, I am Furhat.")

# Pause the script for 3 seconds to give Furhat time to actually speak
time.sleep(3)

furhat.disconnect()
