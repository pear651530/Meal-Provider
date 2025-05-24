import requests
import json

# 設定 API 的基礎 URL
BASE_URL = "http://localhost:8002"
# 設定新增菜單 API 的端點 URL
ADD_MENU_ITEM_URL = f"{BASE_URL}/menu-items/"
# 設定取得菜單 API 的端點 URL (需要菜品 ID)
GET_MENU_ITEM_URL = f"{BASE_URL}/menu-items/"
# 設定取得所有菜單 API 的端點 URL
GET_ALL_MENU_ITEMS_URL = f"{BASE_URL}/menu-items/"
# 設定菜單變更 API 的端點 URL
MENU_CHANGES_URL = f"{BASE_URL}/menu-changes/"
# 設定管理員的 Bearer Token (請替換為你實際使用的 token，如果你的 API 需要驗證)
ADMIN_TOKEN = "your-secret-admin-token"
# 設定刪除菜單 API 的端點 URL (需要菜品 ID)
DELETE_MENU_ITEM_URL = f"{BASE_URL}/menu-items/"

# 設定請求的 Headers
headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

def test_add_menu_item(payload):
    """
    測試新增單筆菜單項目的功能。

    Args:
        payload (dict): 要新增的菜單項目的資料 (符合 schemas.MenuItemCreate)。

    Returns:
        dict or None: 如果新增成功，返回回應的 JSON 內容；否則返回 None。
    """
    print("\n[測試] 新增單筆菜單...")
    try:
        response = requests.post(ADD_MENU_ITEM_URL, headers=headers, json=payload)
        response.raise_for_status()
        print("  新增菜單請求成功！")
        print("  回應狀態碼:", response.status_code)
        response_json = response.json()
        print("  回應內容:", response_json)
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"  新增菜單請求失敗: {e}")
        if response is not None:
            print("  回應狀態碼:", response.status_code)
            print("  回應內容:", response.text)
        return None

def test_get_menu_item(item_id):
    """
    測試取得單筆菜單項目的功能。

    Args:
        item_id (int): 要取得的菜單項目的 ID。

    Returns:
        dict or None: 如果取得成功，返回回應的 JSON 內容；否則返回 None。
    """
    get_url = f"{GET_MENU_ITEM_URL}{item_id}"
    print(f"\n[測試] 取得單筆菜單 (ID: {item_id})...")
    try:
        response = requests.get(get_url, headers=headers)
        response.raise_for_status()
        print(f"  取得菜單 (ID: {item_id}) 請求成功！")
        print("  回應狀態碼:", response.status_code)
        response_json = response.json()
        print("  回應內容:", response_json)
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"  取得菜單 (ID: {item_id}) 請求失敗: {e}")
        if response is not None:
            print("  回應狀態碼:", response.status_code)
            print("  回應內容:", response.text)
        return None

def test_get_all_menu_items():
    """
    測試取得所有菜單項目的功能。

    Returns:
        list or None: 如果取得成功，返回包含所有菜單項目的列表；否則返回 None。
    """
    print("\n[測試] 取得所有菜單...")
    try:
        response = requests.get(GET_ALL_MENU_ITEMS_URL, headers=headers)
        response.raise_for_status()
        print("  取得所有菜單請求成功！")
        print("  回應狀態碼:", response.status_code)
        response_json = response.json()
        print(f"  回應內容 (前 10 個):", response_json[:10]) # 只顯示前 10 個，避免過多輸出
        print(f"  總共有 {len(response_json)} 個菜單項目。")
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"  取得所有菜單請求失敗: {e}")
        if response is not None:
            print("  回應狀態碼:", response.status_code)
            print("  回應內容:", response.text)
        return None

def test_update_menu_item(item_id, payload):
    """
    測試修改菜單項目的功能 (通過 /menu-changes/ 端點)。

    Args:
        item_id (int): 要修改的菜單項目的 ID。
        payload (dict): 包含修改資訊的字典 (符合 schemas.MenuChangeCreate)。

    Returns:
        dict or None: 如果修改成功，返回回應的 JSON 內容；否則返回 None。
    """
    update_url = MENU_CHANGES_URL
    print(f"\n[測試] 修改菜單 (ID: {item_id})...")
    change_payload = {
        "menu_item_id": item_id,
        "change_type": "update",
        "new_values": payload
    }
    try:
        response = requests.post(update_url, headers=headers, json=change_payload)
        response.raise_for_status()
        print(f"  修改菜單 (ID: {item_id}) 請求成功！")
        print("  回應狀態碼:", response.status_code)
        response_json = response.json()
        print("  回應內容:", response_json)
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"  修改菜單 (ID: {item_id}) 請求失敗: {e}")
        if response is not None:
            print("  回應狀態碼:", response.status_code)
            print("  回應內容:", response.text)
        return None

def test_menu():
        # 設定要新增的菜單資料
    new_menu_item_payload = {
        "name": "測試菜單 B",
        "description": "用於驗證修改菜單",
        "price": 139.99,
        "category": "測試"
    }

    # 1. 測試新增單筆菜單 (用於後續修改)
    added_menu = test_add_menu_item(new_menu_item_payload)

    if added_menu and "id" in added_menu:
        added_menu_id = added_menu["id"]

        # 2. 測試取得單筆菜單
        test_get_menu_item(added_menu_id)

        # 3. 測試修改菜單
        update_payload = {
            "name": "修改後的測試菜單 B",
            "price": 149.99
        }
        test_update_menu_item(added_menu_id, update_payload)

        # 4. 再次取得單筆菜單，驗證修改是否成功
        test_get_menu_item(added_menu_id)
        # 5. 測試取得所有菜單
        test_get_all_menu_items()

def del_request(item_id):
    """
    測試刪除單筆菜單項目的功能。

    Args:
        item_id (int): 要刪除的菜單項目的 ID。

    Returns:
        bool: 如果刪除成功返回 True，否則返回 False。
    """
    delete_url = f"{DELETE_MENU_ITEM_URL}{item_id}"
    print(f"\n[測試] 刪除菜單 (ID: {item_id})...")
    try:
        response = requests.delete(delete_url, headers=headers)
        response.raise_for_status()
        print(f"  刪除菜單 (ID: {item_id}) 請求成功！")
        print("  回應狀態碼:", response.status_code)
        response_json = response.json()
        print("  回應內容:", response_json)
        return True
    except requests.exceptions.RequestException as e:
        print(f"  刪除菜單 (ID: {item_id}) 請求失敗: {e}")
        if response is not None:
            print("  回應狀態碼:", response.status_code)
            print("  回應內容:", response.text)
        return False
    
def test_delete():
        # 設定要新增的菜單資料 (用於測試刪除)
    new_menu_item_payload_delete = {
        "name": "測試刪除菜單",
        "description": "用於驗證刪除功能",
        "price": 99.99,
        "category": "測試"
    }

    # 1. 測試新增單筆菜單 (用於後續刪除)
    added_menu_delete = test_add_menu_item(new_menu_item_payload_delete)

    if added_menu_delete and "id" in added_menu_delete:
        added_menu_id_delete = added_menu_delete["id"]
        print(f"\n準備測試刪除 ID 為 {added_menu_id_delete} 的菜單...")
        print("\n<<<<<<<<noe menu>>>>>")
        test_get_all_menu_items()

        # 2. 測試刪除菜單
        delete_successful = del_request(added_menu_id_delete)
        print("\n<<<<<<<<noe menu>>>>>")
        test_get_all_menu_items()

        if delete_successful:
            print(f"\n嘗試獲取 ID 為 {added_menu_id_delete} 的菜單，驗證是否已刪除...")
            # 3. 嘗試獲取已刪除的菜單，預期會失敗
            test_get_menu_item_after_deletion = test_get_menu_item(added_menu_id_delete)
            if test_get_menu_item_after_deletion is None:
                print(f"  驗證成功：ID 為 {added_menu_id_delete} 的菜單已成功刪除。")
            else:
                print(f"  驗證失敗：ID 為 {added_menu_id_delete} 的菜單刪除後仍然可以獲取到！")

if __name__ == "__main__":

    # 測試新增、獲取、修改菜單
    test_menu()
    # 測試刪除菜單
    test_delete()