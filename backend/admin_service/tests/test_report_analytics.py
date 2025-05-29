import pytest
from fastapi.testclient import TestClient
import requests
import re

import sys
import os

# 將專案根目錄加入 sys.path (根據你之前的路徑設定調整)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from admin_service.main import app, verify_admin, ORDER_SERVICE_URL, USER_SERVICE_URL

# 模擬 verify_admin 權限（覆寫）
@pytest.fixture(scope="function")
def client():
    async def override_verify_admin(token: str = "test-token"):
        return {"id": 1, "username": "admin_test", "role": "admin", "token": token}

    app.dependency_overrides[verify_admin] = override_verify_admin

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture
def requests_mock_fixture():
    import requests_mock
    with requests_mock.Mocker() as m:
        yield m

# 判斷是否為 order_trends 查詢
def match_order_trends(request):
    # 確認 path 跟 query string
    if request.path_url.startswith("/api/analytics"):
        qs = request.qs
        return qs.get("report_type") == ["order_trends"] and (qs.get("period") == ["weekly"] or qs.get("report_period") == ["weekly"])
    return False

# 判斷是否為 menu_preferences 查詢
def match_menu_preferences(request):
    if request.path_url.startswith("/api/analytics"):
        qs = request.qs
        return qs.get("report_type") == ["menu_preferences"]
    return False

def test_fetch_analytics_report_with_ratings_success(client, requests_mock_fixture):
    csv_content_order_trends = "item_id,item_name,quantity,income\n1,DishA,10,100.00\n2,DishB,5,50.00\n"
    csv_content_menu_preferences = "total_order_ids,recent_orders_within_period\n10,8\n"

    # mock order_trends
    requests_mock_fixture.register_uri(
        'GET',
        f"{ORDER_SERVICE_URL}/api/analytics",
        additional_matcher=match_order_trends,
        content=csv_content_order_trends.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )

    # mock menu_preferences
    requests_mock_fixture.register_uri(
        'GET',
        f"{ORDER_SERVICE_URL}/api/analytics",
        additional_matcher=match_menu_preferences,
        content=csv_content_menu_preferences.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )

    # mock user ratings
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratingswithorder/1",
        json={"menu_item_id": 1, "menu_item_name": "DishA", "total_reviews": 10, "good_reviews": 8, "good_ratio": 0.75},
        status_code=200
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratingswithorder/2",
        json={"menu_item_id": 2, "menu_item_name": "DishB", "total_reviews": 5, "good_reviews": 3, "good_ratio": 0.64},
        status_code=200
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")

    assert response.status_code == 200
    text = response.text
    lines = text.strip().splitlines()
    print("Response Text:", text)
    assert "item_name" in lines[0]
    assert "DishA" in text
    assert "0.75" in text
    assert "DishB" in text
    assert "0.33" in text

    total_line = lines[-1]
    assert total_line.startswith("TOTAL")
    assert "15" in total_line  # total quantity 10 + 5
    assert "150.00" in total_line  # total income 100 + 50
    assert "11" in total_line  # total_reviews 10 + 5
    assert "7" in total_line  # good_reviews 8 + 3
    assert "0.64" in total_line  # good_ratio

    assert "ERROR:" not in total_line

def test_fetch_analytics_report_with_partial_rating_failures(client, requests_mock_fixture):
    csv_content_order_trends = "item_id,item_name,quantity,income\n1,DishA,10,100.00\n2,DishB,5,50.00\n3,DishC,2,20.00\n"
    csv_content_menu_preferences = "total_order_ids,recent_orders_within_period\n17,12\n"

    requests_mock_fixture.register_uri(
        'GET',
        f"{ORDER_SERVICE_URL}/api/analytics",
        additional_matcher=match_order_trends,
        content=csv_content_order_trends.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )
    requests_mock_fixture.register_uri(
        'GET',
        f"{ORDER_SERVICE_URL}/api/analytics",
        additional_matcher=match_menu_preferences,
        content=csv_content_menu_preferences.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )

    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratingswithorder/1",
        json={"menu_item_id": 1, "menu_item_name": "DishA", "total_reviews": 10, "good_reviews": 8, "good_ratio": 0.8},
        status_code=200
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratingswithorder/2",
        status_code=404
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratingswithorder/3",
        status_code=500
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")

    assert response.status_code == 200
    text = response.text
    lines = text.strip().splitlines()
    assert "DishA" in text
    assert "DishB" in text
    assert "DishC" in text

    total_line = lines[-2]
    assert total_line.startswith("TOTAL")
    assert "17" in total_line  # quantity 10+5+2
    assert "170.00" in total_line  # income 100+50+20

    # 評價只有DishA成功計算
    assert "5" in total_line
    assert "3" in total_line
    assert "0.6" in total_line

    error_line = lines[-1]
    assert error_line.startswith("ERROR:")
    assert "2 menu items failed" in error_line

def test_fetch_analytics_report_default(client, requests_mock_fixture):
    csv_content_order_trends = "item_id,item_name,quantity,income\n1,DishA,10,100.00\n2,DishB,5,50.00\n"
    csv_content_menu_preferences = "total_order_ids,recent_orders_within_period\n10,8\n"

    requests_mock_fixture.register_uri(
        'GET',
        f"{ORDER_SERVICE_URL}/api/analytics",
        additional_matcher=match_order_trends,
        content=csv_content_order_trends.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )
    requests_mock_fixture.register_uri(
        'GET',
        f"{ORDER_SERVICE_URL}/api/analytics",
        additional_matcher=match_menu_preferences,
        content=csv_content_menu_preferences.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )

    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratingswithorder/1",
        json={"menu_item_id": 1, "menu_item_name": "DishA", "total_reviews": 10, "good_reviews": 8, "good_ratio": 0.8},
        status_code=200,
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratingswithorder/2",
        json={"menu_item_id": 2, "menu_item_name": "DishB", "total_reviews": 5, "good_reviews": 3, "good_ratio": 0.6},
        status_code=200,
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")

    assert response.status_code == 200
    assert "DishA" in response.text

def test_fetch_analytics_report_order_service_unavailable(client, requests_mock_fixture):
    # 模擬 ORDER_SERVICE 連線錯誤
    requests_mock_fixture.register_uri(
        'GET',
        re.compile(f"{ORDER_SERVICE_URL}/api/analytics.*"),
        exc=requests.exceptions.ConnectionError,
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")
    assert response.status_code == 503
    assert "Order or Rating service unavailable" in response.text
