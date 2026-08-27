::MQTT Architecture Demo: Local PCs, Broker, Python Backend, Vercel Frontend
::
This demo shows the common production pattern:

```text
Local PC backend 1 --\
Local PC backend 2 ----> MQTT broker ----> Python subscriber backend ----> Vercel frontend
Local PC backend 3 --/
```

The local PCs publish MQTT messages. The Python backend subscribes to the MQTT broker and exposes `/messages` for the frontend. The frontend is a static dashboard that can be hosted on Vercel.

Important: a Vercel frontend cannot access `localhost` on your computer. For Vercel to read your Python backend, the Python backend must have a public URL.

For testing, use:

```text
Frontend on your computer -> http://localhost:3000
```

For real Vercel hosting, use:

```text
Frontend on Vercel -> https://your-public-backend-url.com
```

You can get a public backend URL by deploying the Python backend to a cloud server or by using a tunnel such as ngrok or Cloudflare Tunnel during testing.

## Files

- `cloud_server.py`: MQTT subscriber backend plus HTTP API for the frontend.
- `local_pc_client.py`: one local PC MQTT publisher simulator.
- `publish_dummy_data.py`: sends one batch of dummy MQTT data for `pc-1`, `pc-2`, and `pc-3`.
- `requirements.txt`: Python dependency list.
- `frontend/`: Vercel-ready dashboard frontend.

## Install Python Dependency

This demo uses the MQTT client library `paho-mqtt`.

```powershell
py -m pip install -r requirements.txt
```

If your Python command is `python`, use:

```powershell
python -m pip install -r requirements.txt
```

## Run the MQTT Subscriber Backend

Open one PowerShell terminal:

```powershell
py .\cloud_server.py
```

You should see:

```text
[cloud] listening on http://localhost:3000
[mqtt] connected to broker.hivemq.com:1883
[mqtt] subscribed to rasha/demo/+/data
```

By default this demo uses the public HiveMQ test broker:

```text
broker.hivemq.com:1883
```

For production, use your own broker such as Mosquitto, EMQX, HiveMQ Cloud, or AWS IoT Core.

## Run 3 Local PC MQTT Publishers

Open three more PowerShell terminals.

Terminal 1:

```powershell
$env:PC_ID="pc-1"; py .\local_pc_client.py
```

Terminal 2:

```powershell
$env:PC_ID="pc-2"; py .\local_pc_client.py
```

Terminal 3:

```powershell
$env:PC_ID="pc-3"; py .\local_pc_client.py
```

Each local backend publishes every 2 seconds to MQTT topics:

```text
rasha/demo/pc-1/data
rasha/demo/pc-2/data
rasha/demo/pc-3/data
```

The Python backend subscribes to:

```text
rasha/demo/+/data
```

## Send One Batch of Dummy Data

If you only want to test data passing once, run the backend first:

```powershell
py .\cloud_server.py
```

Then open another PowerShell terminal and run:

```powershell
py .\publish_dummy_data.py
```

This sends three dummy MQTT messages:

```text
pc-1 -> rasha/demo/pc-1/data
pc-2 -> rasha/demo/pc-2/data
pc-3 -> rasha/demo/pc-3/data
```

Then open:

```text
http://localhost:3000/messages
```

## Open the Frontend Locally

Open this file in your browser:

```text
frontend/index.html
```

The frontend reads from:

```text
http://localhost:3000/messages
```

You can change the backend URL in the dashboard input.

## See Raw Backend Data

Open this URL in your browser:

```text
http://localhost:3000/messages
```

Or use PowerShell:

```powershell
Invoke-RestMethod http://localhost:3000/messages
```

## How This Maps to Real Deployment

For local PC MQTT publishers in testing:

```text
MQTT_HOST=broker.hivemq.com
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=rasha/demo
```

For local PC MQTT publishers in production:

```text
MQTT_HOST=your-mqtt-broker.com
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=factory/live
```

Then each local PC runs:

```powershell
$env:PC_ID="pc-1"
$env:MQTT_HOST="your-mqtt-broker.com"
$env:MQTT_TOPIC_PREFIX="factory/live"
py .\local_pc_client.py
```

On your cloud Python backend, subscribe to the same topic prefix:

```powershell
$env:MQTT_HOST="your-mqtt-broker.com"
$env:MQTT_TOPIC="factory/live/+/data"
py .\cloud_server.py
```

For the Vercel frontend:

1. Upload or import this project in Vercel.
2. Set the Vercel project root directory to `frontend`.
3. Deploy it as a static site.
4. Open the deployed frontend URL.
5. Put your public Python backend URL into the dashboard input, for example:

```text
https://your-cloud-server.com
```

The dashboard will call:

```text
https://your-cloud-server.com/messages
```

## Online and Offline PCs

The frontend counts a PC as connected only when its latest MQTT message was received in the last 10 seconds.

If a PC stops publishing, it stays in the PC summary but changes to:

```text
offline
```

The connected PC count will go down automatically.

## Backend CORS

The Python backend allows browser requests. For local demo it uses:

```text
ALLOWED_ORIGIN=*
```

For production, set it to your Vercel domain:

```powershell
$env:ALLOWED_ORIGIN="https://your-project.vercel.app"
py .\cloud_server.py
```

## Why This Works

- Local PCs only make outbound MQTT connections.
- No router port forwarding is needed.
- The MQTT broker receives live messages from all local PCs.
- The Python backend subscribes to MQTT and stores the latest data in one place.
- The Vercel frontend only displays data from the Python backend.
- `pcId` tells the cloud which PC sent the data.

For real production, use TLS MQTT, broker username/password or certificates, retries, and a database instead of in-memory storage.
