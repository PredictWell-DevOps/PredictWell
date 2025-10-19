Render deployment notes

Use this repository's `server:app` ASGI application as the entrypoint.

Recommended web process (Procfile):

web: gunicorn server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 2

Tips:
- Ensure `requirements.txt` includes `gunicorn` and `uvicorn[standard]`.
- Render sets $PORT automatically; bind to 0.0.0.0:$PORT in the Procfile.
- Configure a health check at `/healthz` (exists) or `/`.
- If you place app modules under `backend/`, keep `Procfile` entry as `server:app` (the root `server.py` dynamically loads router modules).

Render project root note:
- On Render you can set the "Root Directory" for a service. If your service Root Directory is `backend/`, Render will look for `requirements.txt` and `Procfile` there. To support either choice this repository includes `backend/requirements.txt` (which references the top-level file) and `backend/Procfile` as a fallback.

Local development (Windows):

- Use uvicorn for local dev rather than gunicorn on Windows:
	C:/path/to/venv/Scripts/python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000
- On Linux/Render the Procfile will run gunicorn which is not available on Windows as an exe wrapper; Render will install gunicorn from `requirements.txt` and run it.

Health checks:
- Use `/healthz` which returns {"status": "ok"}.
- Configure Render's health check to hit `/healthz` (HTTP) every 10s with a 2s timeout.
