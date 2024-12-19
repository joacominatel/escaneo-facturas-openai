from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from databases.db import Base
from datetime import datetime

class InvoiceData(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(String)
    bill_to = Column(String)
    billing_period = Column(String)
    currency = Column(String)
    date = Column(String)
    invoice_number = Column(String)
    invoice_total = Column(String)
    items = Column(JSON)
    payment_terms = Column(String)
    subtotal = Column(String)
    vat = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<InvoiceData {self.invoice_number}>"
    
    def __str__(self):
        return f"<InvoiceData {self.invoice_number}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "bill_to": self.bill_to,
            "billing_period": self.billing_period,
            "currency": self.currency,
            "date": self.date,
            "invoice_number": self.invoice_number,
            "invoice_total": self.invoice_total,
            "items": self.items,
            "payment_terms": self.payment_terms,
            "subtotal": self.subtotal,
            "vat": self.vat,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def save_invoice_data(session, invoice_data):
        """Saves the invoice data to the database.

        Args:
            session: A SQLAlchemy session object.
            invoice_data: A dictionary containing the invoice data in JSON format.
        """

        try:
            # Create InvoiceData object from dictionary
            invoice = InvoiceData(
                invoice_number=invoice_data.get("invoice_number"),
                amount=invoice_data.get("amount", None) and float(invoice_data["amount"]),
                bill_to=invoice_data.get("bill_to"),
                billing_period=invoice_data.get("billing_period"),
                currency=invoice_data.get("currency"),
                date=invoice_data.get("date") and datetime.strptime(invoice_data["date"], "%d-%b-%Y"),  # Parse date format
                invoice_total=invoice_data.get("invoice_total", None) and float(invoice_data["invoice_total"]),
                items=invoice_data.get("items"),
                payment_terms=invoice_data.get("payment_terms"),
                subtotal=invoice_data.get("subtotal", None) and float(invoice_data["subtotal"]),
                vat=invoice_data.get("vat", None) and float(invoice_data["vat"]),
            )

            # Add and commit the changes
            session.add(invoice)
            session.commit()
            print(f"Invoice {invoice.invoice_number} saved successfully!")

        except Exception as e:
            print(f"Error saving invoice data: {e}")
            session.rollback()