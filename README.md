# Simple Flask API

A minimal Flask API with one endpoint.

## Endpoint

| Method | Path     | Description          |
|--------|----------|----------------------|
| GET    | `/items` | Returns list of items |

## Run Locally

```bash
# 1. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API
python app/api.py

# 4. Run tests
pytest
```

## Project Structure

```
.
├── app/
│   └── api.py
├── tests/
│   └── test_api_basic.py
├── requirements.txt
└── README.md
```
