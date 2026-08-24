 Multiple Local Backends, Python Backend, Vercel Frontend Demo

This demo shows the common production pattern:

```text
Local PC backend 1 --\
Local PC backend 2 ----> Python backend ----> Vercel frontend reads data
Local PC backend 3 --/
```

The local PCs send data to a Python backend. The frontend is a static dashboard that can be hosted on Vercel.

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

- `cloud_server.py`: the cloud-hosted backend receiver.
- `local_pc_client.py`: one local PC backend simulator.
- `frontend/`: Vercel-ready dashboard frontend.

## Run the Cloud Backend

Open one PowerShell terminal:

```powershell
python .\cloud_server.py
```

You should see:

```text
[cloud] listening on http://localhost:3000
```

## Run 3 Local PC Backends

Open three more PowerShell terminals.

Terminal 1:

```powershell
$env:PC_ID="pc-1"; python .\local_pc_client.py
```

Terminal 2:

```powershell
$env:PC_ID="pc-2"; python .\local_pc_client.py
```

Terminal 3:

```powershell
$env:PC_ID="pc-3"; python .\local_pc_client.py
```

Each local backend sends data every 2 seconds to:

```text
http://localhost:3000/data
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

For local PC clients in testing:

```text
CLOUD_URL=http://localhost:3000/data
```

For local PC clients in production:

```text
CLOUD_URL=https://your-cloud-server.com/data
```

Then each local PC runs:

```powershell
$env:PC_ID="pc-1"
$env:CLOUD_URL="https://your-cloud-server.com/data"
$env:API_KEY="your-real-secret"
python .\local_pc_client.py
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

## Backend CORS

The Python backend allows browser requests. For local demo it uses:

```text
ALLOWED_ORIGIN=*
```

For production, set it to your Vercel domain:

```powershell
$env:ALLOWED_ORIGIN="https://your-project.vercel.app"
python .\cloud_server.py
```

## Why This Works

- Local PCs only make outbound internet requests.
- No router port forwarding is needed.
- The Python backend receives all data in one place.
- The Vercel frontend only displays data from the Python backend.
- `pcId` tells the cloud which PC sent the data.
- `x-api-key` is a simple demo authentication method.

For real production, use HTTPS, stronger authentication, retries, and a database instead of in-memory storage.
