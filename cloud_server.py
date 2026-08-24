from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from datetime import datetime, timezone


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "3000"))
API_KEY = os.environ.get("API_KEY", "demo-secret")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

received_messages = []


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
            self.send_json(
                200,
                {
                    "ok": True,
                    "service": "cloud-backend",
                    "storedMessages": len(received_messages),
                },
            )
            return

        if self.path == "/messages":
            self.send_json(
                200,
                {
                    "count": len(received_messages),
                    "messages": received_messages,
                },
            )
            return

        self.send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        if self.path != "/data":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return

        if self.headers.get("x-api-key") != API_KEY:
            self.send_json(401, {"ok": False, "error": "Invalid API key"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body.decode("utf-8"))
        except Exception as error:
            self.send_json(400, {"ok": False, "error": str(error)})
            return

        pc_id = data.get("pcId")
        if not isinstance(pc_id, str) or not pc_id:
            self.send_json(400, {"ok": False, "error": "Missing pcId"})
            return

        message = {
            "id": len(received_messages) + 1,
            "receivedAt": now_iso(),
            "remoteAddress": self.client_address[0],
            **data,
        }
        received_messages.append(message)

        print(
            f"[cloud] received #{message['id']} from {pc_id}: "
            f"{json.dumps(data.get('payload', {}))}",
            flush=True,
        )

        self.send_json(201, {"ok": True, "storedId": message["id"]})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), CloudHandler)
    print(f"[cloud] listening on http://localhost:{PORT}", flush=True)
    print("[cloud] POST local backend data to /data", flush=True)
    print("[cloud] open /messages to see received data", flush=True)
    server.serve_forever()
