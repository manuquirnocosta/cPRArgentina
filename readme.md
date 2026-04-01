# cPRArgentina

ABO-adjusted cPRA calculator based on Argentine donor data.

This project is a small FastAPI web app with a built-in HTML frontend. A user can enter unacceptable HLA antigens and an ABO blood group, and the app returns an estimated cPRA based on a local SQLite donor dataset.

## Current scope

- Prototype for research and validation
- Not intended for direct clinical decision-making
- Supports demo and real SQLite datasets
- Includes two calculation modes: `freq` and `filter`

## Main endpoints

- `GET /` serves the frontend
- `POST /calc_cpra` calculates cPRA
- `GET /dataset_info` returns dataset metadata
- `GET /reference_data` returns valid HLA antigens and supported options
- `GET /health` returns a simple service health response
- `POST /reload_db` reloads the database into memory

## Local run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
uvicorn main:app --reload
```

3. Open:

```text
http://127.0.0.1:8000
```

## Database selection

By default, the app uses `cpra_demo.db`.

To use another SQLite file, set:

```bash
CPRA_DB=cpra.db
```

On Windows PowerShell:

```powershell
$env:CPRA_DB="cpra.db"
uvicorn main:app --reload
```

## Environment variables

- `CPRA_DB`: SQLite database filename or path
- `CPRA_CORS_ORIGINS`: comma-separated allowed origins, default `*`

Example:

```text
CPRA_DB=cpra_demo.db
CPRA_CORS_ORIGINS=https://tu-dominio.onrender.com
```

## Demo dataset

You can recreate the synthetic demo database with:

```bash
python init_demo_db.py
```

If `cpra_demo.db` is missing at startup, the app now recreates it automatically.

## Deploy-ready notes

This repo is prepared for simple deployment:

- `Dockerfile` included
- health endpoint included
- frontend served by FastAPI itself
- SQLite database kept outside Git

Important:

- Do not commit the real donor database
- For a prototype, SQLite is acceptable if you run a single small web service
- For production-grade scale or stricter reliability, a more robust database setup would be better

## Suggested deployment flow

1. Deploy using `cpra_demo.db`
2. Confirm the public site loads and calculates correctly
3. Upload or mount the real SQLite database on the server
4. Point `CPRA_DB` to the real file
5. Restrict `CPRA_CORS_ORIGINS` to the final public URL

## Render quick start

This repo includes `render.yaml` for a simple first deployment on Render.

Expected settings:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Default demo DB: generated automatically if missing

For the first public prototype, deploy with the demo DB and only switch to the real dataset after the site is stable.

## Pre-deploy checklist

- App starts successfully
- `/health` returns `status: ok`
- Frontend loads at `/`
- A valid cPRA example returns a result
- Invalid antigen input returns a readable error
- Demo dataset metadata appears in the interface
- Disclaimer is visible in the UI

## Disclaimer

Research Use Only.

This tool is intended for research, methodological validation, and educational purposes. It is not intended for direct clinical decision-making without independent verification.
