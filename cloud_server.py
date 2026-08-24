from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import threading
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "3000"))
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
MQTT_HOST = os.environ.get("MQTT_HOST", "broker.hivemq.com")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "rasha/demo/+/data")
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")

received_messages = []
messages_lock = threading.Lock()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


class CloudHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, x-api-key")
        super().end_headers()

    def send_json(self, status_code, data):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            with messages_lock:
                stored_messages = len(received_messages)

            self.send_json(
                200,
                {
                    "ok": True,
                    "service": "mqtt-subscriber-backend",
                    "mqttHost": MQTT_HOST,
                    "mqttTopic": MQTT_TOPIC,
                    "storedMessages": stored_messages,
                },
            )
            return

        if self.path == "/messages":
            with messages_lock:
                messages = list(received_messages)

            self.send_json(
                200,
                {
                    "count": len(messages),
                    "messages": messages,
                },
            )
            return

        self.send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        self.send_json(
            405,
            {
                "ok": False,
                "error": "This backend receives device data from MQTT. Use GET /messages for the frontend.",
            },
        )

    def log_message(self, format, *args):
        return


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[mqtt] connected to {MQTT_HOST}:{MQTT_PORT}", flush=True)
        client.subscribe(MQTT_TOPIC)
        print(f"[mqtt] subscribed to {MQTT_TOPIC}", flush=True)
    else:
        print(f"[mqtt] connect failed: {reason_code}", flush=True)


def on_message(client, userdata, mqtt_message):
    try:
        data = json.loads(mqtt_message.payload.decode("utf-8"))
    except Exception as error:
        print(f"[mqtt] invalid message on {mqtt_message.topic}: {error}", flush=True)
        return

    pc_id = data.get("pcId")
    if not isinstance(pc_id, str) or not pc_id:
        print(f"[mqtt] ignored message without pcId on {mqtt_message.topic}", flush=True)
        return

    with messages_lock:
        message = {
            "id": len(received_messages) + 1,
            "receivedAt": now_iso(),
            "mqttTopic": mqtt_message.topic,
            **data,
        }
        received_messages.append(message)

    print(
        f"[mqtt] received #{message['id']} from {pc_id}: "
        f"{json.dumps(data.get('payload', {}))}",
        flush=True,
    )


def start_mqtt_subscriber():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=start_mqtt_subscriber, daemon=True)
    mqtt_thread.start()

    server = HTTPServer((HOST, PORT), CloudHandler)
    print(f"[cloud] listening on http://localhost:{PORT}", flush=True)
    print("[cloud] frontend reads MQTT data from /messages", flush=True)
    server.serve_forever()
