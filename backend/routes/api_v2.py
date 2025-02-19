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
from config.socketio_instance import socketio

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

    # Se espera que el frontend envíe el 'socket_id' para direccionar los mensajes
    socket_id = request.form.get("socket_id") or request.args.get("socket_id")

    results = []
    session = SessionLocal()

    try:
        for file in files:
            if file.filename == '':
                log_action = "analyze_error"
                log_message = "Nombre de archivo vacío"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                if socket_id:
                    socketio.emit('progress', {
                        'status': 'error',
                        'filename': '',
                        'message': 'Nombre de archivo vacío'
                    }, room=socket_id)
                continue

            if not allowed_file(file.filename):
                log_action = "analyze_error"
                log_message = f"Formato de archivo no permitido. Solo se permiten: {ALLOWED_EXTENSIONS}"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                if socket_id:
                    socketio.emit('progress', {
                        'status': 'error',
                        'filename': file.filename,
                        'message': f'Formato de archivo no permitido. Solo se permiten: {ALLOWED_EXTENSIONS}'
                    }, room=socket_id)
                continue

            if file.content_length > MAX_FILE_SIZE:
                log_action = "analyze_error"
                log_message = f"El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE / (1024 * 1024)} MB)"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                if socket_id:
                    socketio.emit('progress', {
                        'status': 'error',
                        'filename': file.filename,
                        'message': f'El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE / (1024 * 1024)} MB)'
                    }, room=socket_id)
                continue

            # Enviar mensaje de inicio para esta factura
            if socket_id:
                socketio.emit('progress', {
                    'status': 'start',
                    'filename': file.filename,
                    'message': f'Inicio procesamiento de {file.filename}'
                }, room=socket_id)

            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                images = convert_from_path(file_path)
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

                # Enviar mensaje de finalización con los datos de la factura
                if socket_id:
                    socketio.emit('progress', {
                        'status': 'completed',
                        'filename': file.filename,
                        'message': f'Finalizó procesamiento de {file.filename}',
                        'data': result
                    }, room=socket_id)
            except Exception as e:
                log_action = "analyze_error"
                log_message = f"Error al procesar el archivo {file.filename}: {e}"
                log_category = "error"
                save_log(session, log_action, log_message, log_category)
                error_result = {"error": f"Error al procesar el archivo {file.filename}: {e}"}
                results.append(error_result)
                if socket_id:
                    socketio.emit('progress', {
                        'status': 'error',
                        'filename': file.filename,
                        'message': f'Error al procesar el archivo {file.filename}: {e}'
                    }, room=socket_id)

            try:
                save_invoice_data(session, result)
                session.commit()
            except Exception as e:
                log_action = "analyze_error"
                log_category = "error"
                log_message = f"Error al guardar la factura {result.get('invoice_number')}: {str(e)}"
                save_log(session, log_action, log_message, log_category)
                error_result = {"error": f"Error al guardar la factura {result.get('invoice_number')}: {str(e)}"}
                results.append(error_result)
                if socket_id:
                    socketio.emit('progress', {
                        'status': 'error',
                        'filename': file.filename,
                        'message': f'Error al guardar la factura {result.get("invoice_number")}: {str(e)}'
                    }, room=socket_id)
    except Exception as e:
        log_action = "general_error"
        log_message = f"Error general durante el procesamiento: {str(e)}"
        log_category = "error"
        save_log(session, log_action, log_message, log_category)
        results.append({"error": f"Error general durante el procesamiento: {str(e)}"})
        if socket_id:
            socketio.emit('progress', {
                'status': 'error',
                'message': f'Error general durante el procesamiento: {str(e)}'
            }, room=socket_id)
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

@api_v2.route('/api_v2/invoices', methods=['GET'])
def get_invoices():
    """
    Endpoint de la API para obtener todas las facturas.

    Args:
        offset (query param): El número de resultados a omitir (para paginación).
        limit (query param): El número máximo de resultados a devolver.

    Returns:
        Una respuesta JSON que contiene una lista de todas las facturas o un mensaje de error.
    """
    from databases.models.invoice import InvoiceData

    try:
        offset = int(request.args.get('offset', default=0))
        limit = int(request.args.get('limit', default=20))
        if offset < 0 or limit < 0:
            raise ValueError("Los parámetros offset y limit deben ser mayores o iguales a 0.")
    except ValueError as e:
        return jsonify({'error': str(e), 'message': 'Los parámetros offset y limit deben ser números enteros'}), 400
    
    session = SessionLocal()
    invoices = session.query(InvoiceData).order_by(InvoiceData.id.desc()).offset(offset).limit(limit).all()

    if invoices:
        invoice_list = [invoice.serialize() for invoice in invoices]
        session.close()
        return jsonify(invoice_list), 200
    
    session.close()
    return jsonify({'error': 'No se encontraron facturas'}), 404

@api_v2.route('/api_v2/invoices/invoice_number/<invoice_number>', methods=['GET'])
def get_invoice(invoice_number):
    """
    Endpoint de la API para buscar una factura por su número.

    Args:
        invoice_number: El número de factura a buscar.

    Returns:
        Una respuesta JSON que contiene la factura o un mensaje de error.
    """
    from databases.models.invoice import InvoiceData

    session = SessionLocal()
    invoice = session.query(InvoiceData).filter(InvoiceData.invoice_number == invoice_number).first()

    if invoice:
        invoice_data = invoice.serialize()
        session.close()
        return jsonify(invoice_data), 200
    
    session.close()
    return jsonify({'error': f"No se encontró la factura con el número {invoice_number}"}), 404


@api_v2.route('/api_v2/invoices/<op>', methods=['GET'])
def get_invoice_by_op(op):
    """
    Endpoint de la API para buscar facturas que contengan un número de publicidad específico.

    Args:
        advertising_number: El número de publicidad a buscar.
        offset (query param): El número de resultados a omitir (para paginación).
        limit (query param): El número máximo de resultados a devolver.

    Returns:
        Una respuesta JSON que contiene una lista de facturas coincidentes o un mensaje de error.    
    """
    from modules.search_op import search_invoices_by_advertising_order

    session = SessionLocal()
    try:
        offset = int(request.args.get('offset', default=0))
        limit = int(request.args.get('limit', default=20))
        if offset < 0 or limit < 0:
            raise ValueError("Los parámetros offset y limit deben ser mayores o iguales a 0.")
        
    except ValueError as e:
        session.close()
        return jsonify({'error': str(e), 'message': 'Los parámetros offset y limit deben ser números enteros'}), 400
    
    invoices, total = search_invoices_by_advertising_order(session, op, offset, limit)

    if invoices:
        invoice_list = [invoice.serialize() for invoice in invoices]
        session.close()
        return jsonify({'total': total, 'invoices': invoice_list}), 200
    else:
        session.close()
        return jsonify({'error': f"No se encontraron facturas con el número de publicidad {op}"}), 404