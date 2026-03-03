# CI/CD Practice Project

A minimal Flask REST API built to demonstrate a complete CI/CD pipeline: automated testing, Docker environment promotion, feature flags, performance testing, and observability with Prometheus + Grafana.

---

## Goals

- Build and test a Flask API with pytest (unit + edge cases + feature flag tests)
- Containerize with Docker and promote across staging → production environments
- Automate CI with GitHub Actions (test, build, push, performance)
- Simulate feature flag rollout using environment variables
- Instrument metrics with Prometheus and visualize with Grafana

---

## Endpoint

| Method | Path       | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/items`   | Returns list of items (+ feature flag field in staging) |
| GET    | `/metrics` | Prometheus metrics scrape endpoint   |

---

## Project Structure

```
.
├── app/
│   ├── api.py               # Flask app with Prometheus metrics
│   └── Dockerfile
├── tests/
│   ├── conftest.py          # Shared pytest fixtures
│   ├── test_api_basic.py    # Unit + edge case tests
│   └── test_feature_flag_envs.py  # Parametrized env/flag tests
├── performance/
│   └── locustfile.py        # Locust performance test
├── monitoring/
│   └── prometheus.yml       # Prometheus scrape config
├── docs/
│   └── pipeline_design.md   # Pipeline architecture diagram
├── .github/
│   ├── workflows/ci.yml     # GitHub Actions CI/CD pipeline
│   └── pull_request_template.md
├── docker-compose.yml               # Base (test service)
├── docker-compose.staging.yml       # Staging: PORT=5001, flag=true
├── docker-compose.prod.yml          # Production: PORT=5002, flag=false
├── docker-compose.monitoring.yml    # Prometheus + Grafana
├── .env.example             # Env var template (safe to commit)
├── requirements.txt
└── pytest.ini
```

---

## Local Run Instructions

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API (staging config)
$env:ENV="staging"; $env:PORT="5001"; $env:FEATURE_NEW_CHECKOUT="true"
python app/api.py

# 4. Run tests
pytest
```

---

## Docker — Environment Promotion

```bash
# Staging (port 5001, feature flag ON)
docker compose -f docker-compose.staging.yml up --build -d
curl http://localhost:5001/items

# Production (port 5002, feature flag OFF)
docker compose -f docker-compose.prod.yml up --build -d
curl http://localhost:5002/items

# View logs
docker compose -f docker-compose.staging.yml logs -f web
```

---

## Feature Flags

Controlled via `FEATURE_NEW_CHECKOUT` env var:

| Environment | Flag value | `/items` response |
|---|---|---|
| Staging | `true` | Includes `"new_feature": true` on each item |
| Production | `false` | Standard response only |

```bash
# Simulate ON
$env:FEATURE_NEW_CHECKOUT="true"; python app/api.py
curl http://localhost:5000/items
# → [{"id":1,"name":"Item Satu","new_feature":true}, ...]

# Run parametrized flag tests
pytest tests/test_feature_flag_envs.py -v
```

---

## CI/CD Pipeline Summary

| Job | Trigger | Purpose |
|---|---|---|
| `test` | All pushes + PRs | 17 pytest tests, JUnit XML + HTML artifacts, PR comment |
| `build-and-push` | Push to `main` | Docker image → `ghcr.io` |
| `performance` | Push to `main` or manual | Locust 50 users / 60s, report artifact |

See [docs/pipeline_design.md](docs/pipeline_design.md) for architecture diagram.

---

## Performance Testing (Locust)

```bash
# Start API
$env:ENV="staging"; $env:PORT="5001"; python app/api.py

# Headless (same as CI)
locust -f performance/locustfile.py --host http://localhost:5001 `
  --headless -u 50 -r 10 --run-time 60s --html reports/locust-report.html

# Web UI → http://localhost:8089
locust -f performance/locustfile.py --host http://localhost:5001
```

---

## Observability (Prometheus + Grafana)

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

| Service    | URL                          |
|------------|------------------------------|
| Flask API  | http://localhost:5001        |
| /metrics   | http://localhost:5001/metrics |
| Prometheus | http://localhost:9090        |
| Grafana    | http://localhost:3000 (admin/admin) |

**Grafana setup:** Connections → Prometheus → `http://prometheus:9090` → Save & test

**Example PromQL queries:**
```promql
rate(api_requests_total[1m])
histogram_quantile(0.95, rate(api_request_latency_seconds_bucket[1m]))
```

---

## CI/CD Workflow Practice

This project demonstrates a real PR → CI fail → fix → pass → merge cycle.

1. Created `feature/broken-test` → broke code intentionally → CI failed with `AssertionError: expected 3 but got 2`
2. Applied fix → CI passed → merged only after green CI ✅
3. Branch protection on `main` ensures CI must pass before merge is allowed

**Key takeaway:** Never merge a PR while CI is red.

