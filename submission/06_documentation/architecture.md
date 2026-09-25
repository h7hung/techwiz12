# AssureX Web App Architecture

## Application Flow

```text
React Frontend
        |
        v
FastAPI Backend
        |
        v
SQLite Database
        |
        v
Python ML + Decision Engine
        |
        v
Final Decision
```

## Components

### React Frontend

The React frontend will provide the web application interface and render Claim Summary Cards dynamically from text and structured claim data. It will not persist Claim Summary Card images as PNG or JPG files.

### FastAPI Backend

The FastAPI backend will expose the application API, coordinate claim analysis, access SQLite, and invoke the Python ML and decision-engine components.

### SQLite Database

The database will store:

- claim information
- evidence information
- analysis result
- ML prediction
- ML confidence
- final decision
- rule reasons
- timestamps

### Python ML and Decision Engine

The backend will pass claim data to the trained Python ML model and decision engine. Their outputs will be combined into the final decision returned by the application.

## GTM Runtime Flow

```text
Claim text/data
        |
        v
Generate visual representation in memory
        |
        v
GTM prediction
        |
        v
Discard temporary image
```

The GTM runtime may generate a temporary visual representation in memory when required for prediction. The temporary image must be discarded after prediction and must never be persisted to disk or included in the web-app directories.

## Runtime Storage Policy

The web app uses SQLite for structured claim and analysis data. It has no runtime image storage. Existing training and evaluation Claim Summary Card images remain competition evidence and are not modified or copied into the web-app directories.

## Implementation Status

The backend and frontend are intentionally not implemented in this restructuring step. This document defines the target architecture for the later implementation.
