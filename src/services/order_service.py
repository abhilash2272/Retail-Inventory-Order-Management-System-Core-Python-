# src/services/order_service.py
from typing import List, Dict
from src.dao.order_dao import OrderDAO
from src.services.customer_service import CustomerService, CustomerError
from src.services.product_service import ProductService, ProductError

class OrderError(Exception):
    pass

class OrderService:
    def __init__(self, order_dao: OrderDAO, customer_service: CustomerService, product_service: ProductService):
        self.dao = order_dao
        self.customer_service = customer_service
        self.product_service = product_service

    def create_order(self, customer_id: int, items: List[Dict]) -> Dict:
        customer = self.customer_service.dao.get_customer_by_id(customer_id)
        if not customer:
            raise OrderError(f"Customer {customer_id} does not exist")
        total_amount = 0
        validated_items = []

        # Check stock for each product
        for item in items:
            prod = self.product_service.dao.get_product_by_id(item["prod_id"])
            if not prod:
                raise OrderError(f"Product {item['prod_id']} does not exist")
            if prod["stock"] < item["quantity"]:
                raise OrderError(f"Not enough stock for product {prod['name']}")
            validated_items.append({
                "prod_id": prod["prod_id"],
                "quantity": item["quantity"],
                "price": prod["price"]
            })
            total_amount += prod["price"] * item["quantity"]

        # Deduct stock
        for item in validated_items:
            new_stock = self.product_service.dao.get_product_by_id(item["prod_id"])["stock"] - item["quantity"]
            self.product_service.dao.update_product(item["prod_id"], {"stock": new_stock})

        order = self.dao.create_order(customer_id, total_amount)

        # Insert order items
        self.dao.create_order_items(order["order_id"], validated_items)

        return self.dao.get_order_details(order["order_id"])

    def cancel_order(self, order_id: int) -> Dict:
        order_detail = self.dao.get_order_details(order_id)
        if not order_detail:
            raise OrderError("Order not found")
        if order_detail["order"]["status"] != "PLACED":
            raise OrderError("Only orders with status 'PLACED' can be cancelled")

        # Restore stock
        for item in order_detail["items"]:
            prod = self.product_service.dao.get_product_by_id(item["prod_id"])
            new_stock = prod["stock"] + item["quantity"]
            self.product_service.dao.update_product(item["prod_id"], {"stock": new_stock})

        # Update status
        return self.dao.update_order_status(order_id, "CANCELLED")

    def complete_order(self, order_id: int) -> Dict:
        order_detail = self.dao.get_order_details(order_id)
        if not order_detail:
            raise OrderError("Order not found")
        if order_detail["order"]["status"] != "PLACED":
            raise OrderError("Only orders with status 'PLACED' can be completed")
        return self.dao.update_order_status(order_id, "COMPLETED")

    def get_order_details(self, order_id: int) -> Dict:
        order_detail = self.dao.get_order_details(order_id)
        if not order_detail:
            raise OrderError("Order not found")
        return order_detail

    def list_orders_of_customer(self, customer_id: int) -> List[Dict]:
        return self.dao.list_orders_by_customer(customer_id)
