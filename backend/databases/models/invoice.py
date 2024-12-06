from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from databases.db import Base
from datetime import datetime

class InvoiceData(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String, index=True)
    manufacturer_location = Column(String, index=True, nullable=True)
    invoice_number = Column(String, index=True)
    invoice_date = Column(DateTime, index=True)
    billing_period = Column(String, index=True)
    account_id = Column(String, index=True, nullable=True)
    payment_terms = Column(String, index=True, nullable=True)
    bill_to = Column(String, index=True, nullable=True)
    bill_to_location = Column(String, index=True, nullable=True)
    advertiser = Column(String, index=True)
    items = Column(JSON(String), index=True)
    subtotal = Column(Float, index=True)
    total = Column(Float, index=True)
    vat_rate = Column(Float, index=True, nullable=True)
    vat_amount = Column(Float, index=True, nullable=True)
    bank_details = Column(String, index=True, nullable=True)
    currency = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<InvoiceData(id={self.id}, manufacturer={self.manufacturer}, invoice_number={self.invoice_number}, invoice_date={self.invoice_date}, total={self.total})>"
    
    def __str__(self):
        return f"{self.manufacturer} - {self.invoice_number} - {self.invoice_date} - {self.total}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "manufacturer": self.manufacturer,
            "manufacturer_location": self.manufacturer_location,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "billing_period": self.billing_period,
            "account_id": self.account_id,
            "payment_terms": self.payment_terms,
            "bill_to": self.bill_to,
            "bill_to_location": self.bill_to_location,
            "advertiser": self.advertiser,
            "items": self.items,
            "subtotal": self.subtotal,
            "total": self.total,
            "vat_rate": self.vat_rate,
            "vat_amount": self.vat_amount,
            "bank_details": self.bank_details,
            "currency": self.currency,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
