import os
from flask import request, jsonify, Blueprint
from werkzeug.utils import secure_filename
import tempfile
import pytesseract
from PIL import Image
import io
from pdf2image import convert_from_path
from modules.assistant_v2 import analyze_text, allowed_file

api_v2 = Blueprint("api_v2", __name__)

UPLOAD_FOLDER = tempfile.mkdtemp()
api_v2.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024

@api_v2.route('/api/analyze', methods=['POST'])
def analyze():
    if 'files' not in request.files:
        return jsonify({'error': 'No se han proporcionado archivos'}), 400

    files = request.files.getlist('files')
    if not files:
      return jsonify({'error': 'No se han proporcionado archivos'}), 400
    
    results = []

    for file in files:
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': f'Formato de archivo no permitido. Solo se permiten: {ALLOWED_EXTENSIONS}'}), 400

        if file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': f'El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE / (1024 * 1024)} MB)'}), 400
        
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(api_v2.config['UPLOAD_FOLDER'], filename)
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
        except Exception as e:
            results.append({"error": f"Error al procesar el archivo {file.filename}: {e}"})
            print(f"Error al procesar archivo: {e}")

    return jsonify(results), 200