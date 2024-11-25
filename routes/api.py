from flask import Blueprint, request, jsonify
import os
from datetime import datetime

api = Blueprint("api", __name__)

@api.route("/health", methods=["GET"])
def health():
    return "OK"

@api.route("/api/process_invoices", methods=["POST"])
def process_invoices():
    """
    This should receive a PDF file and return the extracted invoice data as JSON.
    """
    from modules.ia import process_invoice

    try:
        pdf_file = request.files["file"]
        # validation
        if pdf_file and pdf_file.filename.split(".")[-1] in ["pdf", "PDF", "zip", "ZIP", "7z"]:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_filename = f"{timestamp}_{pdf_file.filename}"
            save_path = os.path.join("../uploads", new_filename)

            pdf_file.save(save_path)

            invoice_data = process_invoice(save_path)
            return jsonify(invoice_data)
        else:
            return "Error: Archivo no válido. Por favor, suba un archivo PDF o ZIP."
    except Exception as e:
        return f"Error procesando facturas: {e}"
