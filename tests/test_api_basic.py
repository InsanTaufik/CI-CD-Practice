from unittest.mock import patch


# -- Success cases ------------------------------------------------------------

def test_get_items_status_200(client):
    """Endpoint GET /items harus mengembalikan status 200."""
    response = client.get("/items")
    print(f"[INFO] Status respons: {response.status_code}")
    assert response.status_code == 200


def test_get_items_returns_list(client):
    """Endpoint GET /items harus mengembalikan sebuah list JSON."""
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] Data diterima: {data}")
    assert isinstance(data, list)


def test_get_items_not_empty(client):
    """Daftar item tidak boleh kosong."""
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] Jumlah item: {len(data)}")
    assert len(data) > 0


def test_get_items_structure(client):
    """Setiap item harus memiliki field 'id' dan 'name'."""
    response = client.get("/items")
    data = response.get_json()
    for item in data:
        print(f"[INFO] Memeriksa item: {item}")
        assert "id" in item
        assert "name" in item


def test_get_items_content_type_json(client):
    """Respons harus bertipe application/json."""
    response = client.get("/items")
    print(f"[INFO] Content-Type: {response.content_type}")
    assert "application/json" in response.content_type


def test_get_items_exact_count(client):
    """Daftar item harus memiliki tepat 3 item."""
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] Jumlah item: {len(data)} (diharapkan: 3)")
    assert len(data) == 3, f"expected 3 but got {len(data)}"


# -- Edge cases ---------------------------------------------------------------

def test_get_items_empty_list(client):
    """Ketika daftar item kosong, endpoint harus mengembalikan list kosong []."""
    with patch("app.api.ITEMS", []):
        response = client.get("/items")
        data = response.get_json()
        print(f"[INFO] Data saat list kosong: {data}")
        assert response.status_code == 200
        assert data == []


def test_unknown_route_returns_404(client):
    """Rute yang tidak dikenal harus mengembalikan status 404."""
    response = client.get("/tidak-ada")
    print(f"[INFO] Status untuk rute tidak dikenal: {response.status_code}")
    assert response.status_code == 404


def test_404_response_has_error_key(client):
    """Respons 404 harus memiliki field 'error' dalam JSON."""
    response = client.get("/tidak-ada")
    data = response.get_json()
    print(f"[INFO] Isi respons 404: {data}")
    assert data is not None
    assert "error" in data


# -- Feature flag tests (parametrized) ---------------------------------------

import pytest


@pytest.mark.parametrize("flag_value,expect_field", [
    ("true",  True),
    ("false", False),
])
def test_feature_flag_new_checkout(client, monkeypatch, flag_value, expect_field):
    """Parametrized: validasi perilaku FEATURE_NEW_CHECKOUT=true/false."""
    monkeypatch.setenv("FEATURE_NEW_CHECKOUT", flag_value)
    response = client.get("/items")
    data = response.get_json()
    print(f"[INFO] FEATURE_NEW_CHECKOUT={flag_value} → item[0]: {data[0]}")
    assert response.status_code == 200
    if expect_field:
        for item in data:
            assert item.get("new_feature") is True, (
                f"Diharapkan 'new_feature'=True saat flag=true, dapat: {item}"
            )
    else:
        for item in data:
            assert "new_feature" not in item, (
                f"'new_feature' tidak boleh ada saat flag=false, dapat: {item}"
            )
