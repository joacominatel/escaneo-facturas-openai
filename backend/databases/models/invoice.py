from sqlalchemy import Column, Integer, String, DateTime, JSON
from databases.db import Base
from datetime import datetime
from databases.models.log import LogData
from modules.save_log import save_log

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
    """Saves the invoice data to the database, handling string conversions.

    Args:
        session: A SQLAlchemy session object.
        invoice_data: A dictionary containing the invoice data.
    """
    try:
        # Helper function to safely convert strings to floats
        def safe_float_conversion(value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                value = value.replace(",", "")  # Remove commas
                value = value.replace("%", "")    #Remove %
                try:
                    return float(value)
                except ValueError:
                    print(f"Warning: Could not convert '{value}' to float.")
                    return None  # Or handle the error differently, e.g., raise an exception
            return None

        # Helper function to safely convert strings to date time
        def safe_date_conversion(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                try:
                    return datetime.strptime(value, "%d-%b-%Y")
                except ValueError:
                    print(f"Warning: Could not convert '{value}' to datetime.")
                    return None
            return None
        
        if invoice_data.get("invoice_number") is None:
            print("No se ha proporcionado un número de factura.")
            # terminar la ejecución de la función
            return {
                "error": "No se ha proporcionado un número de factura."
            }
        
        # Verificar si ya existe una factura con el mismo número
        existing_invoice = session.query(InvoiceData).filter_by(invoice_number=invoice_data.get("invoice_number")).first()

        if existing_invoice:
            save_log(session, "save_invoice", f"La factura {invoice_data.get('invoice_number')} ya existe en la base de datos.", "warning")
            print(f"La factura {invoice_data.get('invoice_number')} ya existe en la base de datos.")
            return {
                "error": f"La factura {invoice_data.get('invoice_number')} ya existe en la base de datos."
            }

        invoice = InvoiceData(
            invoice_number=invoice_data.get("invoice_number"),
            amount=safe_float_conversion(invoice_data.get("amount")),
            bill_to=invoice_data.get("bill_to"),
            billing_period=invoice_data.get("billing_period"),
            currency=invoice_data.get("currency"),
            date=safe_date_conversion(invoice_data.get("date")),
            invoice_total=safe_float_conversion(invoice_data.get("invoice_total")),
            items=invoice_data.get("items"),
            payment_terms=invoice_data.get("payment_terms"),
            subtotal=safe_float_conversion(invoice_data.get("subtotal")),
            vat=safe_float_conversion(invoice_data.get("vat")),
        )

        session.add(invoice)
        session.commit()
        print(f"Invoice {invoice.invoice_number} saved successfully!")

        # Log the successful save
        try:
            save_log(session, "save_invoice", f"La factura {invoice.invoice_number} se ha guardado correctamente.", "info")
        except Exception as e:
            session.rollback()
            print(f"Error saving log data: {e}")
    except Exception as e:
        session.rollback()
        print(f"Error saving invoice data: {e}")
        raise e
    finally:
        session.close()