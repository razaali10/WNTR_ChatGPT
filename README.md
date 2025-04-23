# WNTR EPANET Simulation API

A FastAPI web service for simulating EPANET models using WNTR. Upload a `.inp` file and receive summary stats and plots in return.

## Endpoint

- **POST /simulate**: Upload `.inp` file → receive JSON summary + base64 plot

## Run Locally

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 7860
```