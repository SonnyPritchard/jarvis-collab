# jarvis-collab

Shared workspace for Sonny + Corey Jarvis federation experiments.

## Quick start: federation router

A drop-in FastAPI router is included at `federation_router.py`.

### Mount in your app

```python
from fastapi import FastAPI
from federation_router import router as federation_router

app = FastAPI()
app.include_router(federation_router)
```

### Required env vars

- `FEDERATION_API_KEY`
- `FEDERATION_HMAC_SECRET`
- `INSTANCE_ID`
- `INSTANCE_NAME`

### Endpoints provided

- `GET /federation/capabilities`
- `POST /federation/negotiate`
- `POST /federation/result`
- `POST /federation/progress`
- `GET /federation/progress/{task_id}`

Shared workspace for Sonny + Corey Jarvis federation experiments
