"""
performance/locustfile.py

Locust performance test for GET /items endpoint.
Run locally:
    locust -f performance/locustfile.py --host http://localhost:5001

Headless (CI):
    locust -f performance/locustfile.py --host http://localhost:5001 \
        --headless -u 50 -r 10 --run-time 1m \
        --html reports/locust-report.html \
        --csv reports/locust
"""

from locust import HttpUser, task, between


class ItemsUser(HttpUser):
    """Simulasi pengguna yang mengakses endpoint /items."""

    # Waktu tunggu antara setiap request: 1–3 detik
    wait_time = between(1, 3)

    @task(3)
    def get_items(self):
        """Hit GET /items — bobot 3 (paling sering dipanggil)."""
        with self.client.get("/items", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if not isinstance(data, list):
                    response.failure(
                        f"Diharapkan list, dapat: {type(data).__name__}"
                    )
                elif len(data) == 0:
                    response.failure("Daftar item kosong — tidak diharapkan")
                else:
                    response.success()
            else:
                response.failure(
                    f"Status tidak terduga: {response.status_code}"
                )

    @task(1)
    def get_unknown_route(self):
        """Hit rute tidak dikenal — pastikan 404 ditangani dengan benar."""
        with self.client.get("/tidak-ada", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
            else:
                response.failure(
                    f"Diharapkan 404, dapat: {response.status_code}"
                )
