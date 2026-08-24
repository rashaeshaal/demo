import json
import os
import random
import socket
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


PC_ID = os.environ.get("PC_ID") or "pc-1"
MQTT_HOST = os.environ.get("MQTT_HOST", "broker.hivemq.com")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.environ.get("MQTT_TOPIC_PREFIX", "rasha/demo")
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")
INTERVAL_SECONDS = float(os.environ.get("INTERVAL_SECONDS") or "2")

sequence = 0


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def random_metric(min_value, max_value):
    return round(random.uniform(min_value, max_value), 2)


def build_message():
    global sequence
    sequence += 1

    return {
        "pcId": PC_ID,
        "sentAt": now_iso(),
        "sequence": sequence,
        "payload": {
            "machineName": socket.gethostname(),
            "temperature": random_metric(25, 90),
            "pressure": random_metric(1, 5),
            "status": "running" if random.random() > 0.1 else "warning",
        },
    }


def main():
    topic = f"{MQTT_TOPIC_PREFIX}/{PC_ID}/data"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    print(f"[{PC_ID}] connecting to MQTT broker {MQTT_HOST}:{MQTT_PORT}", flush=True)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    print(f"[{PC_ID}] publishing data to topic {topic}", flush=True)

    while True:
        message = build_message()
        result = client.publish(topic, json.dumps(message), qos=1)
        result.wait_for_publish()

        print(f"[{PC_ID}] published #{message['sequence']} to MQTT", flush=True)

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
