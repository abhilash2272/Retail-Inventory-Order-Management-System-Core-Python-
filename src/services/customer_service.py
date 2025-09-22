from typing import List, Dict
from src.dao.customer_dao import CustomerDAO


class CustomerError(Exception):
    """Custom exception for customer validation or business rules."""
    pass


class CustomerService:
    """Service layer for customer-related operations."""

    def __init__(self, dao: CustomerDAO):
        self.dao = dao

    def add_customer(self, name: str, email: str, phone: str, city: str | None = None) -> Dict:
        # Validate unique email
        if self.dao.get_customer_by_email(email):
            raise CustomerError(f"Email already exists: {email}")
        return self.dao.create_customer(name, email, phone, city)

    # Update phone or city 
    def update_customer(self, cust_id: int, phone: str | None = None, city: str | None = None) -> Dict:
        customer = self.dao.get_customer_by_id(cust_id)
        if not customer:
            raise CustomerError("Customer not found")
        fields = {}
        if phone:
            fields["phone"] = phone
        if city:
            fields["city"] = city
        if not fields:
            raise CustomerError("No fields to update")
        return self.dao.update_customer(cust_id, fields)

    def delete_customer(self, cust_id: int) -> Dict:
        customer = self.dao.get_customer_by_id(cust_id)
        if not customer:
            raise CustomerError("Customer not found")
        if self.dao.customer_has_orders(cust_id):
            raise CustomerError("Cannot delete customer with existing orders")
        return self.dao.delete_customer(cust_id)

    def list_customers(self, limit: int = 100) -> List[Dict]:
        return self.dao.list_customers(limit=limit)

    # Search customers by email or city 
    def search_customers(self, email: str | None = None, city: str | None = None) -> List[Dict]:
        return self.dao.search_customers(email=email, city=city)
