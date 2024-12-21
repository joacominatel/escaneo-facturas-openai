import os
from flask import request, jsonify, Blueprint
from werkzeug.utils import secure_filename
import tempfile
import pytesseract
from PIL import Image
import io
from pdf2image import convert_from_path
from modules.assistant_v2 import analyze_text, allowed_file
from databases.db import SessionLocal, init_db
from databases.models.invoice import save_invoice_data
from modules.save_log import save_log


api_v2 = Blueprint("api_v2", __name__)

# Inicializar la base de datos
init_db()

UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024

@api_v2.route('/api_v2/analyze', methods=['POST'])
def analyze():
    if 'files' not in request.files:
        return jsonify({'error': 'No se han proporcionado archivos'}), 400

    files = request.files.getlist('files')
    if not files:
      return jsonify({'error': 'No se han proporcionado archivos'}), 400
    
    results = []
    session = SessionLocal()

    try:
        for file in files:
            if file.filename == '':
                log_action = "analyze_error"
                log_message = "Nombre de archivo vacío"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                return jsonify({'error': 'Nombre de archivo vacío'}), 400

            if not allowed_file(file.filename):
                log_action = "analyze_error"
                log_message = f"Formato de archivo no permitido. Solo se permiten: {ALLOWED_EXTENSIONS}"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                return jsonify({'error': f'Formato de archivo no permitido. Solo se permiten: {ALLOWED_EXTENSIONS}'}), 400

            if file.content_length > MAX_FILE_SIZE:
                log_action = "analyze_error"
                log_message = f"El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE / (1024 * 1024)} MB)"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                return jsonify({'error': f'El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE / (1024 * 1024)} MB)'}), 400
            
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                images = convert_from_path(file_path, poppler_path=r'C:\\poppler-24.08.0\\Library\\bin')
                text = ""
                for image in images:
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    image = Image.open(io.BytesIO(img_byte_arr))
                    text += pytesseract.image_to_string(image, lang='spa')

                result = analyze_text(text) 
                results.append(result)
                os.remove(file_path)
            except Exception as e:
                log_action = "analyze_error"
                log_message = f"Error al procesar el archivo {file.filename}: {e}"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                results.append({"error": f"Error al procesar el archivo {file.filename}: {e}"})
                print(f"Error al procesar archivo: {e}")

            try:
                save_invoice_data(session, result)
                session.commit()
            except Exception as e:
                log_action = "analyze_error"
                log_category = "error"
                log_message = f"Error al guardar la factura {result.get('invoice_number')}: {str(e)}"
                save_log(session, log_action, log_message, log_category)
                results.append({"error": f"Error al guardar la factura {result.get('invoice_number')}: {str(e)}"})
    except Exception as e:
        log_action = "general_error"
        log_message = f"Error general durante el procesamiento: {str(e)}"
        log_category = "error"
        save_log(session, log_action, log_message, log_category)
        results.append({"error": f"Error general durante el procesamiento: {str(e)}"})
    finally:
        session.close()

    return jsonify(results), 200

@api_v2.route('/api_v2/logs', methods=['GET'])
def get_logs():
    from databases.models.log import LogData

    session = SessionLocal()
    logs = session.query(LogData).all()
    session.close()
    return jsonify([log.serialize() for log in logs]), 200