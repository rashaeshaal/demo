import json
import os
import random
import socket
import time
from datetime import datetime, timezone
from urllib import request
from urllib.error import URLError, HTTPError


PC_ID = os.environ.get("PC_ID") or "pc-1"
CLOUD_URL = os.environ.get("CLOUD_URL") or "http://localhost:3000/data"
API_KEY = os.environ.get("API_KEY") or "demo-secret"
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


def send_message(message):
    body = json.dumps(message).encode("utf-8")
    http_request = request.Request(
        CLOUD_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "x-api-key": API_KEY,
        },
    )

    with request.urlopen(http_request, timeout=10) as response:
        return response.status, response.read().decode("utf-8")


def main():
    print(f"[{PC_ID}] sending data to {CLOUD_URL}", flush=True)

    while True:
        message = build_message()

        try:
            status_code, _ = send_message(message)
            print(
                f"[{PC_ID}] sent #{message['sequence']} -> cloud responded {status_code}",
                flush=True,
            )
        except HTTPError as error:
            print(
                f"[{PC_ID}] cloud rejected #{message['sequence']}: {error.code}",
                flush=True,
            )
        except URLError as error:
            print(
                f"[{PC_ID}] send failed #{message['sequence']}: {error.reason}",
                flush=True,
            )

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
