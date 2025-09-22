# src/dao/payment_dao.py
from typing import List, Dict, Optional
from src.config import get_supabase

class PaymentDAO:
    def __init__(self):
        self.sb = get_supabase()

    def create_payment(self, order_id: int, amount: float, method: str = None, status: str = "PENDING") -> Optional[Dict]:
        payload = {"order_id": order_id, "amount": amount, "method": method, "status": status}
        self.sb.table("payments").insert(payload).execute()
        resp = self.sb.table("payments").select("*").eq("order_id", order_id).order("payment_id", desc=True).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_payment_status(self, payment_id: int, status: str, method: str = None) -> Optional[Dict]:
        fields = {"status": status}
        if method:
            fields["method"] = method
        self.sb.table("payments").update(fields).eq("payment_id", payment_id).execute()
        resp = self.sb.table("payments").select("*").eq("payment_id", payment_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_payment_by_order(self, order_id: int) -> Optional[Dict]:
        resp = self.sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None
