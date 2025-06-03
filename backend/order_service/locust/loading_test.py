from locust import HttpUser, between, task

menu_item_dict = {
    "en_name": "Test Menu Item",
    "zh_name": "測試菜單項目",
    "price": 10.0,
    "is_available": True,
    "url": "http://example.com/image.png"
}

class OrderServiceUser(HttpUser):
    wait_time = between(1, 3)

    #@task
    #def create_menu_item(self):
    #    self.client.post("/menu-items/", json=menu_item_dict)

    @task
    def get_menu_items(self):
        self.client.get("/menu-items/")

    #@task
    #def create_order(self):
    #    order_data = {
    #        "user_id": 1,
    #        "payment_method": "credit_card",
    #        "items": [
    #            {
    #                "menu_item_id": 1,
    #                "quantity": 2
    #            }
    #        ]
    #    }
    #    self.client.post("/orders/", json=order_data)