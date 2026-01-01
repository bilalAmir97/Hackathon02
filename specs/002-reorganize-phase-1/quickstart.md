# Quickstart: Phase I Reorganization

This guide explains how to run and verify the reorganized Phase I application.

## Prerequisites
- Python 3.9+
- Assets must be moved to the `Phase I/` directory.

## Verification Steps

### 1. Change Directory
Navigate into the new Phase I root:
```bash
cd "Phase I"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Tests
Verify structural integrity:
```bash
python -m pytest tests/
```

### 4. Run Application
Verify the application launches correctly:
```bash
python -m src.cli.app_controller
```

## Troubleshooting
If you encounter `ModuleNotFoundError`, ensure you are running the `python` commands from the **root of the `Phase I/` directory**.
