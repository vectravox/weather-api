#!/usr/bin/env python3
"""Weather API server entry point.

This script starts the FastAPI application using Uvicorn.
It is the main entry point for the Weather API service.

Usage:
    python3 script.py

The server will start at http://127.0.0.1:8000
Documentation is available at /docs and /redoc.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
