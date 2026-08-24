import json
import os
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


MQTT_HOST = os.environ.get("MQTT_HOST", "broker.hivemq.com")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.environ.get("MQTT_TOPIC_PREFIX", "rasha/demo")
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def dummy_messages():
    return [
        {
            "pcId": "pc-1",
            "sequence": 1,
            "sentAt": now_iso(),
            "payload": {
                "machineName": "packing-line-pc",
                "temperature": 42.5,
                "pressure": 2.1,
                "status": "running",
            },
        },
        {
            "pcId": "pc-2",
            "sequence": 1,
            "sentAt": now_iso(),
            "payload": {
                "machineName": "mixing-line-pc",
                "temperature": 56.8,
                "pressure": 3.4,
                "status": "running",
            },
        },
        {
            "pcId": "pc-3",
            "sequence": 1,
            "sentAt": now_iso(),
            "payload": {
                "machineName": "quality-check-pc",
                "temperature": 78.2,
                "pressure": 4.6,
                "status": "warning",
            },
        },
    ]


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    print(f"[dummy] connecting to MQTT broker {MQTT_HOST}:{MQTT_PORT}", flush=True)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    time.sleep(1)

    for message in dummy_messages():
        topic = f"{MQTT_TOPIC_PREFIX}/{message['pcId']}/data"
        result = client.publish(topic, json.dumps(message), qos=1)
        result.wait_for_publish()
        print(f"[dummy] published {message['pcId']} to {topic}", flush=True)

    client.loop_stop()
    client.disconnect()
    print("[dummy] finished publishing dummy MQTT data", flush=True)


if __name__ == "__main__":
    main()
