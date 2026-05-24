from __future__ import annotations

import time
import uuid
from typing import Any

import pytest
import requests


def _random_user() -> tuple[str, str, str]:
    suffix = uuid.uuid4().hex[:10]
    username = f"e2e_{suffix}"
    email = f"{username}@example.com"
    password = "Qwerty123!"
    return username, email, password


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _required_product_payload(category_id: int) -> dict[str, Any]:
    return {
        "name": f"E2E Product {int(time.time())}",
        "description": "E2E should reject non-admin write",
        "brand": "E2E",
        "price": 9999.0,
        "currency": "RUB",
        "inStock": True,
        "stockQuantity": 1,
        "categoryId": category_id,
        "componentType": "OTHER",
        "socket": None,
        "supportedSockets": [],
        "ramType": None,
        "gpuTdp": 0,
        "cpuTdp": 0,
        "psuWatts": 0,
        "supportsWifi": False,
        "scoreGaming": 1.0,
        "scoreWork": 1.0,
        "scoreStudy": 1.0,
        "scoreGeneral": 1.0,
        "notes": "e2e"
    }


@pytest.mark.e2e
def test_full_user_flow(base_url: str, http: requests.Session, call) -> None:
    username, email, password = _random_user()

    register_response = call(
        http,
        "POST",
        f"{base_url}/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert register_response.status_code == 201, register_response.text
    register_body = register_response.json()
    assert register_body["user"]["username"] == username
    token = register_body["token"]
    assert token

    login_response = call(
        http,
        "POST",
        f"{base_url}/api/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    login_body = login_response.json()
    assert login_body["tokenType"] == "Bearer"
    login_token = login_body["token"]

    me_response = call(http, "GET", f"{base_url}/api/auth/me", headers=_auth_headers(login_token))
    assert me_response.status_code == 200, me_response.text
    me_body = me_response.json()
    assert me_body["username"] == username
    assert me_body["email"] == email.lower()

    products_response = call(http, "GET", f"{base_url}/api/products", params={"inStock": "true", "size": 5})
    assert products_response.status_code == 200, products_response.text
    products_body = products_response.json()
    assert products_body["items"], "Expected non-empty product catalog"
    first_product = products_body["items"][0]

    order_payload = {
        "items": [
            {
                "productId": first_product["id"],
                "productName": first_product["name"],
                "quantity": 1,
                "unitPrice": first_product["price"],
            }
        ],
        "note": "E2E order",
        "currency": "RUB",
    }
    create_order_response = call(
        http,
        "POST",
        f"{base_url}/api/orders",
        headers=_auth_headers(login_token),
        json=order_payload,
    )
    assert create_order_response.status_code == 201, create_order_response.text
    created_order = create_order_response.json()
    assert created_order["status"] == "CREATED"
    assert created_order["items"][0]["productId"] == first_product["id"]
    order_id = created_order["id"]

    my_orders_response = call(http, "GET", f"{base_url}/api/orders", headers=_auth_headers(login_token))
    assert my_orders_response.status_code == 200, my_orders_response.text
    my_orders = my_orders_response.json()
    assert any(order["id"] == order_id for order in my_orders)

    order_response = call(http, "GET", f"{base_url}/api/orders/{order_id}", headers=_auth_headers(login_token))
    assert order_response.status_code == 200, order_response.text
    loaded_order = order_response.json()
    assert loaded_order["id"] == order_id
    assert loaded_order["username"] == username


@pytest.mark.e2e
def test_ai_configurator_flow(base_url: str, http: requests.Session, call) -> None:
    username, email, password = _random_user()
    register_response = call(
        http,
        "POST",
        f"{base_url}/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert register_response.status_code == 201, register_response.text
    token = register_response.json()["token"]

    payload = {
        "budget": 200000,
        "purpose": "gaming",
        "preferred_brand": "any",
        "needs_wifi": False,
        "target_resolution": "1080p",
        "min_ram_gb": 16,
    }
    response = call(
        http,
        "POST",
        f"{base_url}/api/configurator/recommend",
        headers=_auth_headers(token),
        json=payload,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["purpose"] == "gaming"
    assert body["total_price"] <= payload["budget"]
    assert len(body["components"]) == 7


@pytest.mark.e2e
def test_non_admin_cannot_manage_products(base_url: str, http: requests.Session, call) -> None:
    username, email, password = _random_user()
    register_response = call(
        http,
        "POST",
        f"{base_url}/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert register_response.status_code == 201, register_response.text
    token = register_response.json()["token"]

    categories_response = call(http, "GET", f"{base_url}/api/products/categories")
    assert categories_response.status_code == 200, categories_response.text
    categories = categories_response.json()
    assert categories, "Expected categories for product payload"

    payload = _required_product_payload(categories[0]["id"])
    create_response = call(
        http,
        "POST",
        f"{base_url}/api/products",
        headers=_auth_headers(token),
        json=payload,
    )
    assert create_response.status_code == 403, create_response.text
