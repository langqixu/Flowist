# Flowist Local Development Guidelines

## Standard Ports
To avoid conflicts with other local services, we strictly adhere to the following port assignments:

| Service | Port | Description |
| str | int | text |
| --- | --- | --- |
| **Backend API** | `8000` | FastAPI Server |
| **Frontend Web** | `3001` | Next.js Admin/User Interface |
| **Streamlit (Legacy)** | `8501` | Original PM Demo Interface |

> [!IMPORTANT]
> The Frontend Web (`admin-frontend`) MUST run on **port 3001**.
> Do not use the default Next.js port (3000).

## Quick Start

### Start Frontend (Web)
```bash
# Using helper script (Recommended)
./start_web.sh

# Or manually
cd admin-frontend
npm run dev
```

### Start Backend
```bash
# Using helper script
./start_backend.sh
```
