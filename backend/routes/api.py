from flask import Blueprint, request, jsonify
from datetime import datetime
from databases.db import SessionLocal, init_db
from databases.models.file_record import FileRecord
from modules.assistant import assistant_process_invoices
from sqlalchemy.exc import SQLAlchemyError

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
    # Validate request
    if "files" not in request.files or len(request.files.getlist("files")) == 0:
        return jsonify({"error": "No files uploaded"}), 408

    files = request.files.getlist("files")
    question = request.form.get("question", "Extract the invoice data from the provided text or attachment.")

    if question == "":
        question = "Extract the invoice data from the provided text or attachment."

    # Validate file types
    for file in files:
        if not file.filename.endswith(".pdf") and not file.filename.endswith(".zip"):
            return jsonify({"error": "Only PDF and ZIP files are allowed"}), 415

    # Prepare response data
    response_data = {
        "message": "Files received",
        "files": [file.filename for file in files],
        "question": question,
        "timestamp": datetime.now().isoformat(),
        "processed_data": []
    }

    # Open a database session
    session = SessionLocal()

    # create random float number from pi and exact datetime
    rnd = datetime.now().timestamp() * 3.14159265359
    rnd = rnd - int(rnd)

    try:
        # Save each file record and process with assistant module
        for file in files:
            # Save record in the database
            file_record = FileRecord(
                file_name=file.filename,
                question=question,
                details="Processing",
                rnd=rnd
            )
            session.add(file_record)
            session.commit()
            session.refresh(file_record)

            # Process file using assistant module
            try:
                file_path = f"tmp/{file.filename}"  # Save file temporarily
                file.save(file_path)
            except Exception as e:
                status = "Failed"
                details = str(e)
                file_record.details = details
                file_record.status = status
                session.commit()
                response_data["processed_data"].append({
                    "file_name": file.filename,
                    "file_id": file_record.id,
                    "status": status,
                    "details": details
                })
                return jsonify(response_data), 520

            try:
                assistant_results = assistant_process_invoices(file_path, question)
                status = "Completed"
                details = "Processed successfully"
                print(assistant_results)
            except Exception as e:
                status = "Failed"
                details = str(e)

            # Update database with processing results
            file_record.details = details
            file_record.status = status
            session.commit()

            # Append result to response data
            response_data["processed_data"].append({
                "file_name": file.filename,
                "file_id": file_record.id,
                "status": status,
                "details": details,
                "results": assistant_results
            })

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": f"Database error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500
    finally:
        session.close()

    return jsonify(response_data), 200