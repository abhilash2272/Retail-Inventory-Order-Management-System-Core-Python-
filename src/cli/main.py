# src/cli/main.py
import argparse
import json

# DAOs
from src.dao.product_dao import ProductDAO
from src.dao.customer_dao import CustomerDAO
from src.dao.order_dao import OrderDAO
from src.dao.payment_dao import PaymentDAO

# Services
from src.services.product_service import ProductService
from src.services.customer_service import CustomerService, CustomerError
from src.services.order_service import OrderService
from src.services.payment_service import PaymentService, PaymentError
from src.services.report_service import ReportService


class RetailCLI:
    def __init__(self):
        # Services
        self.product_service = ProductService(ProductDAO())
        self.customer_service = CustomerService(CustomerDAO())
        # Correctly pass OrderDAO instead of ProductDAO
        self.order_service = OrderService(OrderDAO(), CustomerDAO(), self.product_service)
        self.payment_service = PaymentService(PaymentDAO(), self.order_service)
        self.report_service = ReportService()

    # ---------------- Product Commands ----------------
    def cmd_product_add(self, args):
        try:
            p = self.product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
            print("Created product:")
            print(json.dumps(p, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_product_list(self, args):
        ps = self.product_service.dao.list_products(limit=100)
        print(json.dumps(ps, indent=2, default=str))

    # ---------------- Customer Commands ----------------
    def cmd_customer_add(self, args):
        try:
            c = self.customer_service.add_customer(args.name, args.email, args.phone, args.city)
            print("Created customer:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerError as e:
            print("Error:", e)

    def cmd_customer_update(self, args):
        try:
            c = self.customer_service.update_customer(cust_id=args.id, phone=args.phone, city=args.city)
            print("Updated customer:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerError as e:
            print("Error:", e)

    def cmd_customer_delete(self, args):
        try:
            c = self.customer_service.delete_customer(args.id)
            print("Deleted customer:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerError as e:
            print("Error:", e)

    def cmd_customer_list(self, args):
        cs = self.customer_service.list_customers(limit=100)
        print(json.dumps(cs, indent=2, default=str))

    def cmd_customer_search(self, args):
        cs = self.customer_service.search_customers(email=args.email, city=args.city)
        print(json.dumps(cs, indent=2, default=str))

    # ---------------- Order Commands ----------------
    def cmd_order_create(self, args):
        items = []
        for item in args.item:
            try:
                pid, qty = item.split(":")
                items.append({"prod_id": int(pid), "quantity": int(qty)})
            except Exception:
                print("Invalid item format:", item)
                return
        try:
            ord = self.order_service.create_order(args.customer, items)
            print("Order created:")
            print(json.dumps(ord, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_order_show(self, args):
        try:
            o = self.order_service.get_order_details(args.order)
            print(json.dumps(o, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_order_cancel(self, args):
        try:
            o = self.order_service.cancel_order(args.order)
            print("Order cancelled:")
            print(json.dumps(o, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    # ---------------- Payment Commands ----------------
    def cmd_payment_process(self, args):
        try:
            payment = self.payment_service.process_payment(args.order, args.method)
            print("Payment processed:")
            print(json.dumps(payment, indent=2, default=str))
        except PaymentError as e:
            print("Error:", e)

    def cmd_payment_refund(self, args):
        try:
            payment = self.payment_service.refund_payment(args.order)
            print("Payment refunded:")
            print(json.dumps(payment, indent=2, default=str))
        except PaymentError as e:
            print("Error:", e)

    # ---------------- Report Commands ----------------
    def cmd_report_top_products(self, args):
        top = self.report_service.top_selling_products()
        print(json.dumps(top, indent=2, default=str))

    def cmd_report_revenue(self, args):
        revenue = self.report_service.total_revenue_last_month()
        print(f"Total revenue in last month: {revenue}")

    def cmd_report_orders(self, args):
        orders = self.report_service.total_orders_per_customer()
        print(json.dumps(orders, indent=2, default=str))

    def cmd_report_frequent_customers(self, args):
        customers = self.report_service.frequent_customers()
        print(json.dumps(customers, indent=2, default=str))

    # ---------------- CLI Parser ----------------
    def build_parser(self):
        parser = argparse.ArgumentParser(prog="retail-cli")
        sub = parser.add_subparsers(dest="cmd")

        # Product subcommands
        p_prod = sub.add_parser("product", help="product commands")
        pprod_sub = p_prod.add_subparsers(dest="action")
        addp = pprod_sub.add_parser("add")
        addp.add_argument("--name", required=True)
        addp.add_argument("--sku", required=True)
        addp.add_argument("--price", type=float, required=True)
        addp.add_argument("--stock", type=int, default=0)
        addp.add_argument("--category", default=None)
        addp.set_defaults(func=self.cmd_product_add)
        listp = pprod_sub.add_parser("list")
        listp.set_defaults(func=self.cmd_product_list)

        # Customer subcommands
        p_cust = sub.add_parser("customer", help="customer commands")
        cust_sub = p_cust.add_subparsers(dest="action")
        addc = cust_sub.add_parser("add")
        addc.add_argument("--name", required=True)
        addc.add_argument("--email", required=True)
        addc.add_argument("--phone", required=True)
        addc.add_argument("--city", default=None)
        addc.set_defaults(func=self.cmd_customer_add)
        updatec = cust_sub.add_parser("update")
        updatec.add_argument("--id", type=int, required=True)
        updatec.add_argument("--phone", default=None)
        updatec.add_argument("--city", default=None)
        updatec.set_defaults(func=self.cmd_customer_update)
        deletec = cust_sub.add_parser("delete")
        deletec.add_argument("--id", type=int, required=True)
        deletec.set_defaults(func=self.cmd_customer_delete)
        listc = cust_sub.add_parser("list")
        listc.set_defaults(func=self.cmd_customer_list)
        searchc = cust_sub.add_parser("search")
        searchc.add_argument("--email", default=None)
        searchc.add_argument("--city", default=None)
        searchc.set_defaults(func=self.cmd_customer_search)

        # Order subcommands
        p_order = sub.add_parser("order", help="order commands")
        order_sub = p_order.add_subparsers(dest="action")
        createo = order_sub.add_parser("create")
        createo.add_argument("--customer", type=int, required=True)
        createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
        createo.set_defaults(func=self.cmd_order_create)
        showo = order_sub.add_parser("show")
        showo.add_argument("--order", type=int, required=True)
        showo.set_defaults(func=self.cmd_order_show)
        cano = order_sub.add_parser("cancel")
        cano.add_argument("--order", type=int, required=True)
        cano.set_defaults(func=self.cmd_order_cancel)

        # Payment subcommands
        p_pay = sub.add_parser("payment", help="payment commands")
        pay_sub = p_pay.add_subparsers(dest="action")
        process = pay_sub.add_parser("process")
        process.add_argument("--order", type=int, required=True)
        process.add_argument("--method", required=True, help="Cash/Card/UPI")
        process.set_defaults(func=self.cmd_payment_process)
        refund = pay_sub.add_parser("refund")
        refund.add_argument("--order", type=int, required=True)
        refund.set_defaults(func=self.cmd_payment_refund)

        # Report subcommands
        p_report = sub.add_parser("report", help="reporting commands")
        report_sub = p_report.add_subparsers(dest="action")
        report_sub.add_parser("top_products").set_defaults(func=self.cmd_report_top_products)
        report_sub.add_parser("revenue").set_defaults(func=self.cmd_report_revenue)
        report_sub.add_parser("orders").set_defaults(func=self.cmd_report_orders)
        report_sub.add_parser("frequent_customers").set_defaults(func=self.cmd_report_frequent_customers)

        return parser

    # ---------------- CLI Runner ----------------
    def run(self):
        parser = self.build_parser()
        args = parser.parse_args()
        if not hasattr(args, "func"):
            parser.print_help()
            return
        args.func(args)


if __name__ == "__main__":
    cli = RetailCLI()
    cli.run()
