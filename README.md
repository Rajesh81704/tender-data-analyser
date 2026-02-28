# Tender Data Analyser API

Simple FastAPI backend scaffold for the tender data analyser project.

## Features

- **FastAPI app** with a versioned API package structure.
- **Health check endpoint** at `/api/v1/health`.
- **Config module** using Pydantic settings for future environment config.

## Getting started

### 1. Create & activate virtual environment (recommended)

From the project root (`tender-data-analyser-v2`):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

If you use Command Prompt instead of PowerShell:

```cmd
.venv\Scripts\activate.bat
```

### 2. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the development server

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

- **Root docs**: `http://127.0.0.1:8000/docs`
- **Health check**: `http://127.0.0.1:8000/api/v1/health`

## Project structure

```text
tender-data-analyser-v2/
├─ app/
│  ├─ api/
│  │  └─ v1/
│  │     ├─ __init__.py
│  │     └─ routes/
│  │        ├─ __init__.py
│  │        └─ health.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  └─ config.py
│  └─ main.py
├─ tests/
│  ├─ __init__.py
│  └─ test_health.py
├─ requirements.txt
└─ README.md
```

You can now extend this structure with models, database integration, and additional API routes as needed.

