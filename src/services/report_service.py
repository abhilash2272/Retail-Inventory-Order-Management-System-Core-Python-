from src.config import get_supabase
from typing import List, Dict
from datetime import datetime, timedelta

class ReportService:
    def __init__(self):
        self.sb = get_supabase()

    def top_selling_products(self) -> List[Dict]:
        resp = self.sb.table("order_items").select("prod_id, quantity").execute()
        data = resp.data or []
        totals = {}
        for item in data:
            totals[item["prod_id"]] = totals.get(item["prod_id"], 0) + item["quantity"]
        top5 = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{"prod_id": pid, "total_quantity": qty} for pid, qty in top5]

    def total_revenue_last_month(self) -> float:
        last_month = datetime.now() - timedelta(days=30)
        resp = self.sb.table("orders").select("total_amount, order_date").gte("order_date", last_month).execute()
        data = resp.data or []
        return sum(order["total_amount"] for order in data)

    def total_orders_per_customer(self) -> List[Dict]:
        resp = self.sb.table("orders").select("cust_id").execute()
        data = resp.data or []
        counts = {}
        for order in data:
            counts[order["cust_id"]] = counts.get(order["cust_id"], 0) + 1
        return [{"cust_id": cid, "total_orders": cnt} for cid, cnt in counts.items()]

    def frequent_customers(self) -> List[Dict]:
        orders = self.total_orders_per_customer()
        return [c for c in orders if c["total_orders"] > 2]
