import os
from pdf2image import convert_from_path
import pytesseract
import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configurar ruta de Tesseract si es necesario
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_scanned_pdf(file_path):
    """
    Convierte las páginas de un PDF escaneado en imágenes y extrae texto usando OCR.
    """
    try:
        print("Convirtiendo PDF en imágenes...")
        images = convert_from_path(file_path)
        print("Extrayendo texto con OCR...")
        text = ''.join(pytesseract.image_to_string(image) for image in images)
        return text
    except Exception as e:
        return f"Error extrayendo texto: {e}"

def extract_invoice_data_from_text(pdf_text):
    """
    Envía texto extraído a OpenAI para estructurarlo como datos de factura.
    """
    prompt = f"""
    Extract the following information from the provided invoice text:

    - Invoice number
    - Date
    - Amount
    - Currency
    - VAT
    - Billing period
    - Payment terms
    - Bill to
    - Items, including:
    - Description
    - Total of each item
    - Operation numbers (if present in the description, such as "OP123456"). For items with multiple operation numbers, extract all of them. If no operation number is present, this field should be omitted.
    - Subtotal
    - Freight charges
    - VAT rate and amount
    - Invoice total

    Ensure the response is formatted as valid JSON.

    Invoice text:
    {pdf_text}

    """
    print("Analizando texto con OpenAI...")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt, "temperature": 0.2}],
    )
    return response.choices[0].message.content

def process_invoice(file_path):
    """
    Procesa un archivo PDF escaneado, extrae datos de factura y los devuelve como JSON.
    """
    try:
        pdf_text = extract_text_from_scanned_pdf(file_path)
        invoice_data = extract_invoice_data_from_text(pdf_text)
        return invoice_data
    except Exception as e:
        return f"Error procesando factura: {e}"

# Ejemplo de uso
if __name__ == "__main__":
    pdf_folder = "./facturas"
    
    # seleccionar cada archivo en la carpeta de facturas y procesar
    try:
        print("Procesando facturas...")
        
        for pdf_file in os.listdir(pdf_folder):
            if pdf_file.lower().endswith(".pdf"):
                print(f"Procesando {pdf_file}...")
                invoice_data = process_invoice(os.path.join(pdf_folder, pdf_file))
                print("Datos extraídos:")
                print(invoice_data)
                print()
            
            # export as json file
            import json

            with open(f"./Procesados/{pdf_file}.json", "w") as outfile:
                json.dump(invoice_data, outfile)
    except Exception as e:
        print(f"Error: {e}")
