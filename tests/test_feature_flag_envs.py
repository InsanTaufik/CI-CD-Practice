"""
tests/test_feature_flag_envs.py

Simulate staging (flag=true) and production (flag=false) env behavior
using monkeypatch fixtures. Mirrors what CI validates pre-release.
"""

import pytest


# ---------------------------------------------------------------------------
# Fixtures — simulate environment promotion contexts
# ---------------------------------------------------------------------------

@pytest.fixture
def staging_env(monkeypatch):
    """Mensimulasikan variabel lingkungan staging."""
    monkeypatch.setenv("ENV", "staging")
    monkeypatch.setenv("FEATURE_NEW_CHECKOUT", "true")
    monkeypatch.setenv("PORT", "5001")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///db_staging.sqlite")
    print("\n[INFO] Lingkungan staging diaktifkan.")


@pytest.fixture
def prod_env(monkeypatch):
    """Mensimulasikan variabel lingkungan production."""
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("FEATURE_NEW_CHECKOUT", "false")
    monkeypatch.setenv("PORT", "5002")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///db_prod.sqlite")
    print("\n[INFO] Lingkungan production diaktifkan.")


# ---------------------------------------------------------------------------
# Staging tests — FEATURE_NEW_CHECKOUT=true
# ---------------------------------------------------------------------------

def test_staging_items_include_new_feature(client, staging_env):
    """[Staging] Setiap item harus memiliki 'new_feature': True."""
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] Respons staging: {data[0]}")
    assert response.status_code == 200
    for item in data:
        assert item.get("new_feature") is True, (
            f"[Staging] 'new_feature' harus True, dapat: {item}"
        )


def test_staging_returns_non_empty_list(client, staging_env):
    """[Staging] Daftar item tidak boleh kosong."""
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] Jumlah item staging: {len(data)}")
    assert len(data) > 0


# ---------------------------------------------------------------------------
# Production tests — FEATURE_NEW_CHECKOUT=false
# ---------------------------------------------------------------------------

def test_prod_items_exclude_new_feature(client, prod_env):
    """[Prod] Field 'new_feature' tidak boleh ada di response production."""
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] Respons production: {data[0]}")
    assert response.status_code == 200
    for item in data:
        assert "new_feature" not in item, (
            f"[Prod] 'new_feature' tidak boleh ada, dapat: {item}"
        )


def test_prod_returns_non_empty_list(client, prod_env):
    """[Prod] Daftar item tidak boleh kosong."""
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] Jumlah item production: {len(data)}")
    assert len(data) > 0


def test_prod_items_have_required_fields(client, prod_env):
    """[Prod] Setiap item harus memiliki field 'id' dan 'name'."""
    response = client.get("/items")
    data = response.get_json()
    for item in data:
        assert "id" in item
        assert "name" in item


# ---------------------------------------------------------------------------
# Parametrized — both envs in one test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("env_name,flag,expect_new_feature", [
    ("staging",    "true",  True),
    ("production", "false", False),
])
def test_feature_flag_per_environment(client, monkeypatch, env_name, flag, expect_new_feature):
    """Parametrized: validasi flag per lingkungan (staging vs production)."""
    monkeypatch.setenv("ENV", env_name)
    monkeypatch.setenv("FEATURE_NEW_CHECKOUT", flag)
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] ENV={env_name}, FEATURE_NEW_CHECKOUT={flag} → item[0]: {data[0]}")
    assert response.status_code == 200
    for item in data:
        if expect_new_feature:
            assert item.get("new_feature") is True
        else:
            assert "new_feature" not in item
