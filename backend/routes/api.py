from flask import Blueprint, request, jsonify
from datetime import datetime
from databases.db import SessionLocal, init_db
from databases.models.file_record import FileRecord

api = Blueprint("api", __name__)

# Inicializar la base de datos
init_db()

@api.route("/health", methods=["GET"])
def health():
    return "OK"

@api.route("/api/process_invoices", methods=["POST"])
def process_invoices():
    """
    This should receive a PDF/zip file and return the extracted invoice data as JSON.
    Could receive a question too.
    """
    # validate
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 408
    
    if len(request.files.getlist("files")) == 0:
        return jsonify({"error": "No files uploaded"}), 408
    
    # validate if the file is a PDF or ZIP
    for file in request.files.getlist("files"):
        if not file.filename.endswith(".pdf") and not file.filename.endswith(".zip"):
            return jsonify({"error": "Only PDF and ZIP files are allowed"}), 415
    
    # create a new session to store the file records
    session = SessionLocal()
    
    files = request.files.getlist("files")
    question = request.form.get("question", "Extract the invoice data from the provided text or attachment.")

    file_names = [file.filename for file in files]

    response_data = {
        "message": "Files received",
        "files": file_names,
        "question": question,
        "timestamp": datetime.now().isoformat(),
        "processed_data": []
    }

    # rnd will be a random number from datetime to use as a seed
    rnd = datetime.now().timestamp()
    # convert in float
    rnd = float(rnd)
    # transform in totally random number
    rnd = (rnd * 100000) % 1000 + 299 # 299 < rnd < 1299

    try:
        for file in files:
            # save the file
            file_record = FileRecord(
                file_name=file.filename,
                question=question,
                received_date=datetime.now(),
                details="Processing",
                rnd = rnd
            )
            session.add(file_record)
            session.commit()
            session.refresh(file_record)
            response_data["processed_data"].append({
                "file_name": file.filename,
                "file_id": file_record.id,
                "status": "Processing"
            })
    except Exception as e:
        return jsonify({"error": f"Error saving the files: {e}"}), 502
    
    # close the session
    session.close()

    return jsonify(response_data), 200