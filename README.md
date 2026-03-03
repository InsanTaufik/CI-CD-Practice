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

## CI/CD Workflow Practice

This project demonstrates a real PR → CI fail → fix → pass → merge cycle.

### What was practiced

1. **Created branch** `feature/broken-test` from `main`
2. **Added test** `test_get_items_exact_count` to assert exactly 3 items returned
3. **Broke the code** intentionally — removed one entry from `ITEMS` in `app/api.py`
4. **Pushed branch** → GitHub Actions CI triggered → job **failed** with:
   ```
   AssertionError: expected 3 but got 2
   ```
5. **Applied fix** — restored `Item Tiga` to the `ITEMS` list
6. **Commit message used:**
   ```
   fix: restore Item Tiga to ITEMS list so get_items() returns 3 items
   ```
7. **Pushed fix** → CI re-triggered → all **9 tests passed**
8. **Merged PR** into `main` only after CI passed

### Key takeaway

Never merge a PR while CI is red. Branch protection on `main` enforces this automatically.

---

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
