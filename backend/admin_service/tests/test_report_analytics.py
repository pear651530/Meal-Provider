import pytest
from fastapi.testclient import TestClient
import requests
from unittest import mock

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

def test_fetch_analytics_report_with_ratings_success(client, requests_mock_fixture):
    csv_content = "item_id,item_name,quantity,income\n1,DishA,10,100.00\n2,DishB,5,50.00\n"

     # 用正則匹配所有 /api/analytics 路徑，忽略query string
    requests_mock_fixture.get(
        f"{ORDER_SERVICE_URL}/api/analytics?report_type=order_trends&period=weekly",
        content=csv_content.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )

    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratings/1",
        json={"menu_item_id": 1, "menu_item_name": "DishA", "total_reviews": 10, "good_reviews": 8, "good_ratio": 0.8},
        status_code=200
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratings/2",
        json={"menu_item_id": 2, "menu_item_name": "DishB", "total_reviews": 5, "good_reviews": 3, "good_ratio": 0.6},
        status_code=200
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")

    assert response.status_code == 200
    text = response.text
    #print("Response Text:", text)  # Debugging output
    lines = text.strip().splitlines()

    # 檢查標頭與資料列
    assert "item_name" in lines[0]
    assert "DishA" in text
    assert "0.8" in text
    assert "DishB" in text
    assert "0.6" in text

    # ✅ 檢查 TOTAL 行存在且數值正確
    total_line = lines[-1]
    assert total_line.startswith("TOTAL")
    assert "15" in total_line  # total quantity
    assert "150.00" in total_line  # total income
    assert "15" in total_line  # total_reviews
    assert "11" in total_line  # good_reviews
    assert "0.73" in total_line  # good_ratio

    # 不應出現錯誤訊息
    assert "ERROR:" not in total_line


def test_fetch_analytics_report_with_partial_rating_failures(client, requests_mock_fixture):
    csv_content = "item_id,item_name,quantity,income\n1,DishA,10,100.00\n2,DishB,5,50.00\n3,DishC,2,20.00\n"
    requests_mock_fixture.get(
        f"{ORDER_SERVICE_URL}/api/analytics?report_type=order_trends&period=weekly",
        content=csv_content.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )

    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratings/1",
        json={"menu_item_id": 1, "menu_item_name": "DishA", "total_reviews": 10, "good_reviews": 8, "good_ratio": 0.8},
        status_code=200
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratings/2",
        status_code=404
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratings/3",
        status_code=500
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")

    assert response.status_code == 200
    text = response.text
#    print("Response Text:", text)  # Debugging output
    lines = text.strip().splitlines()

    assert "DishA" in text
    assert "DishB" in text
    assert "DishC" in text

    total_line = lines[-2]
    assert total_line.startswith("TOTAL")
    assert "17" in total_line  # quantity 10+5+2
    assert "170.00" in total_line  # income 100+50+20

    # 評價相關只計成功的DishA
    assert "10" in total_line  # total_reviews
    assert "8" in total_line   # good_reviews
    assert "0.8" in total_line  # good_ratio

    error_line = lines[-1]
    assert error_line.startswith("ERROR:")
    assert "2 menu items failed" in error_line

def test_fetch_analytics_report_default(client, requests_mock_fixture):
    csv_content = "item_id,item_name,quantity,income\n1,DishA,10,100.00\n2,DishB,5,50.00\n"
    requests_mock_fixture.get(
        f"{ORDER_SERVICE_URL}/api/analytics?report_type=order_trends&period=weekly",
        content=csv_content.encode("utf-8"),
        status_code=200,
        headers={"Content-Type": "text/csv"},
    )
    ##就算不檢查也要mock rating
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratings/1",
        json={"menu_item_id": 1, "menu_item_name": "DishA", "total_reviews": 10, "good_reviews": 8, "good_ratio": 0.8},
        status_code=200,
    )
    requests_mock_fixture.get(
        f"{USER_SERVICE_URL}/ratings/2",
        json={"menu_item_id": 2, "menu_item_name": "DishB", "total_reviews": 5, "good_reviews": 3, "good_ratio": 0.6},
        status_code=200,
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")# 無參數，使用預設 daily + order_trends

    assert response.status_code == 200
    assert "DishA" in response.text


def test_fetch_analytics_report_order_service_unavailable(client, requests_mock_fixture):
    requests_mock_fixture.get(
        f"{ORDER_SERVICE_URL}/api/analytics?report_type=order_trends&period=weekly",
        exc=requests.exceptions.ConnectionError,
    )

    response = client.get("/report/analytics?report_type=order_trends&report_period=weekly")
    assert response.status_code == 503
    assert "Order or Rating service unavailable" in response.text
