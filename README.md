# Embodied AI Scanner

FastAPI app for scanning AI research and industry sources, storing relevant articles locally, and generating trend and weak-signal reports with OpenAI.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env` before running scans. You can optionally set:

```bash
OPENAI_FAST_MODEL=gpt-5.2-mini
OPENAI_REPORT_MODEL=gpt-5.2
```

## Run

```bash
.venv/bin/python eai_run.py
```

The app starts at `http://127.0.0.1:8000/`.

## Without An API Key

The dashboard can still load existing local articles and reports from `data/scanner.db`. The `Run Scan` action will not start AI analysis until `OPENAI_API_KEY` is configured.

## Test

```bash
.venv/bin/python -m unittest discover
```

## Deploy

The app is ready for platforms that run a Python web process from a GitHub repo. It includes both `Procfile` and `railway.toml`.

Required environment variables:

```bash
OPENAI_API_KEY=...
OPENAI_FAST_MODEL=gpt-5.2-mini
OPENAI_REPORT_MODEL=gpt-5.2
```

Recommended start command:

```bash
python eai_run.py
```

The app stores scan results in local SQLite (`data/scanner.db`). On ephemeral hosts, this database may reset between deploys unless persistent storage is configured.

Do not commit `.env`, local databases, virtual environments, bytecode caches, or `.DS_Store`.
