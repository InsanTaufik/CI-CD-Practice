# Pipeline Design

## Architecture Overview

```
Developer Workstation
        │
        │  git push / open PR
        ▼
┌─────────────────────────────────────────────────────┐
│               GitHub Actions CI                     │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Job: test  (all pushes + PRs)               │   │
│  │                                              │   │
│  │  1. Checkout repo                            │   │
│  │  2. Setup Python 3.11                        │   │
│  │  3. pip install -r requirements.txt          │   │
│  │  4. pytest (17 tests)                        │   │
│  │     ├── Unit tests (GET /items)              │   │
│  │     ├── Edge cases (empty list, 404)         │   │
│  │     └── Feature flag (staging vs prod)       │   │
│  │  5. Upload JUnit XML artifact                │   │
│  │  6. Upload HTML report artifact              │   │
│  │  7. Post PR comment with test summary        │   │
│  └──────────────────────────────────────────────┘   │
│              │ needs: test                          │
│              │ (only on push to main)               │
│              ▼                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Job: build-and-push                         │   │
│  │                                              │   │
│  │  1. docker build (app/Dockerfile)            │   │
│  │  2. docker push → ghcr.io/<repo>:latest      │   │
│  │                   ghcr.io/<repo>:sha-<hash>  │   │
│  └──────────────────────────────────────────────┘   │
│              │ needs: test                          │
│              │ (push to main OR workflow_dispatch)  │
│              ▼                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Job: performance                            │   │
│  │                                              │   │
│  │  1. Start Flask API (ENV=staging, PORT=5001) │   │
│  │  2. locust --headless -u 50 --run-time 60s   │   │
│  │  3. Upload locust HTML + CSV artifacts       │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
              │
              │  merge to main triggers CD
              ▼
┌─────────────────────────────────┐
│        Environment Promotion    │
│                                 │
│  STAGING  (docker-compose)      │
│  ├── PORT=5001                  │
│  ├── FEATURE_NEW_CHECKOUT=true  │
│  └── DATABASE_URL=db_staging    │
│              │                  │
│              │  manual approval │
│              ▼                  │
│  PRODUCTION (docker-compose)    │
│  ├── PORT=5002                  │
│  ├── FEATURE_NEW_CHECKOUT=false │
│  └── DATABASE_URL=db_prod       │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│        Observability Stack      │
│                                 │
│  Flask /metrics (prometheus)    │
│       │                         │
│       ▼                         │
│  Prometheus (port 9090)         │
│   scrapes every 15s             │
│       │                         │
│       ▼                         │
│  Grafana (port 3000)            │
│   dashboards + alerts           │
└─────────────────────────────────┘
```

---

## PR Flow Detail

```
feature/branch
    │
    │ git push
    ▼
GitHub PR opened
    │
    ├── CI: test job runs
    │       ├── PASS → bot comment ✅ + artifacts uploaded
    │       └── FAIL → bot comment ❌ + block merge
    │
    │ (after review + green CI)
    │
    ▼
Merge to main
    │
    ├── CI: test (re-runs on main)
    ├── CI: build-and-push → image to ghcr.io
    └── CI: performance → Locust 50u/60s → report artifact
```

---

## Feature Flag Promotion Flow

```
Code change with new feature
    │
    ├── Deploy to STAGING with FEATURE_NEW_CHECKOUT=true
    │       │
    │       ├── QA tests pass ✅
    │       └── Locust performance baseline OK ✅
    │
    ├── Enable flag in PRODUCTION env
    │       FEATURE_NEW_CHECKOUT=true
    │
    └── Monitor via Prometheus/Grafana
            rate(api_requests_total[1m])
            histogram_quantile(0.95, ...)
```

---

## Key Metrics

| Metric | PromQL | Purpose |
|---|---|---|
| Request rate | `rate(api_requests_total[1m])` | Traffic volume |
| Error rate | `rate(api_requests_total{http_status=~"5.."}[1m])` | 5xx errors |
| p95 latency | `histogram_quantile(0.95, rate(api_request_latency_seconds_bucket[1m]))` | SLA monitoring |

---

## Tech Stack

| Layer | Tool |
|---|---|
| API | Python 3.11 + Flask |
| Testing | pytest + pytest-html |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Performance | Locust |
| Metrics | Prometheus + Grafana |
| Registry | GitHub Container Registry (ghcr.io) |
| Env config | python-dotenv + `.env.*` files |
