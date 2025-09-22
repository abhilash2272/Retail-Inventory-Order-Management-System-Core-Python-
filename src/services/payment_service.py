from src.dao.payment_dao import PaymentDAO
from src.services.order_service import OrderService, OrderError
from typing import Optional,List,Dict

class PaymentError(Exception):
    pass

class PaymentService:
    def __init__(self, payment_dao: PaymentDAO, order_service: OrderService):
        self.dao = payment_dao
        self.order_service = order_service

    def process_payment(self, order_id: int, method: str) -> Dict:
        order = self.order_service.get_order_details(order_id)
        if not order:
            raise PaymentError("Order not found")
        if order["order"]["status"] != "PLACED":
            raise PaymentError("Order cannot be paid; status is not PLACED")

        payment = self.dao.get_payment_by_order(order_id)
        if not payment:
            payment = self.dao.create_payment(order_id, order["order"]["total_amount"])

        self.dao.update_payment_status(payment["payment_id"], "PAID", method)
        self.order_service.complete_order(order_id)
        return self.dao.get_payment_by_order(order_id)

    def refund_payment(self, order_id: int) -> Dict:
        payment = self.dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentError("Payment not found")
        self.dao.update_payment_status(payment["payment_id"], "REFUNDED")
        return self.dao.get_payment_by_order(order_id)
