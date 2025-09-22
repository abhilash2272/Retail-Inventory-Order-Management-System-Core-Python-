# src/dao/order_dao.py
from typing import List, Dict, Optional
from src.config import get_supabase

class OrderDAO:
    def __init__(self):
        self.sb = get_supabase()

    def create_order(self, cust_id: int, total_amount: float, status: str = "PLACED") -> Optional[Dict]:
        payload = {"cust_id": cust_id, "total_amount": total_amount, "status": status}
        self.sb.table("orders").insert(payload).execute()
        resp = self.sb.table("orders").select("*").eq("cust_id", cust_id).order("order_id", desc=True).limit(1).execute()
        return resp.data[0] if resp.data else None

    def create_order_items(self, order_id: int, items: List[Dict]):
        for item in items:
            payload = {"order_id": order_id,"prod_id": item["prod_id"],"quantity": item["quantity"],"price": item["price"]}
            self.sb.table("order_items").insert(payload).execute()

    def get_order_details(self, order_id: int) -> Optional[Dict]:
        resp_order = self.sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
        order = resp_order.data[0] if resp_order.data else None
        if not order:
            return None
        resp_cust = self.sb.table("customers").select("*").eq("cust_id", order["cust_id"]).limit(1).execute()
        customer = resp_cust.data[0] if resp_cust.data else None
        resp_items = self.sb.table("order_items").select("*").eq("order_id", order_id).execute()
        items = resp_items.data or []
        return {"order": order, "customer": customer, "items": items}


    def list_orders_by_customer(self, cust_id: int) -> List[Dict]:
        resp = self.sb.table("orders").select("*").eq("cust_id", cust_id).execute()
        return resp.data or []

    def update_order_status(self, order_id: int, status: str) -> Optional[Dict]:
        self.sb.table("orders").update({"status": status}).eq("order_id", order_id).execute()
        resp = self.sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None
