import openai
import os
import json
import pytesseract
import time, re

ALLOWED_EXTENSIONS = {'pdf'}

# pytesseract config for windows
if os.name == 'nt':
    # C:\Program Files\Tesseract-OCR
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Configurar la clave de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: Variable de entorno OPENAI_API_KEY no definida.")
    exit()

try:
    pytesseract.get_tesseract_version()
except pytesseract.TesseractNotFoundError:
    print("Error: Tesseract no está instalado. Consulta la documentación para la instalación.")
    exit()

def analyze_text(text):
    try:
        instructions = f"""
            Analiza el siguiente texto, que corresponde a una factura. Extrae la siguiente información y devuélvela en formato JSON:

            - **Invoice number**
            - **Date**
            - **Amount**
            - **Currency**
            - **VAT**
            - **Billing Period**
            - **Payment Terms**
            - **Bill to**
            - **Items**: Cada línea de artículo debe incluir:
                - **Description**: Descripción del servicio o producto.
                - **Subtotal**: Importe del subtotal de cada artículo.
                - **Operation Numbers (OP numbers)**: Extrae cualquier número de operación que comience con "OP". Estos pueden ser números independientes (ej., "OP123456") o múltiples entradas. Si no se encuentra ningún número de operación, este campo debe omitirse para ese artículo.
            - **Subtotal**: El subtotal de todos los artículos antes de impuestos.
            - **Invoice total**: El importe total incluyendo impuestos.

            # Formato de salida

            El resultado debe ser exclusivamente un JSON con la siguiente estructura:
            ```json
            {{
                "invoice_number": "N/A",
                "date": "N/A",
                "amount": "N/A",
                "currency": "N/A",
                "vat": "N/A",
                "billing_period": "N/A",
                "payment_terms": "N/A",
                "bill_to": "N/A",
                "items": [
                    {{
                        "description": "N/A",
                        "subtotal": "N/A",
                        "operation_numbers": []
                    }}
                ],
                "subtotal": "N/A",
                "invoice_total": "N/A"
            }}
            ```

            # Notas
            - Verifica las diferentes ubicaciones y formatos potenciales de la información dentro de las facturas.
            - Asegura la correcta interpretación del texto, considerando posibles variaciones en el idioma o formato del documento.
            - Las líneas de artículo pueden no tener siempre números de operación; asegúrate de incluirlos solo si se encuentran.
        """

        assistant = openai.beta.assistants.create(
            model="gpt-3.5-turbo",
            instructions=instructions,
            name="Invoice Analysis Assistant",
            temperature=0.3
        )

        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text
        )
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        while run.status != "completed":
            run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(1)

        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        raw_response = messages.data[0].content[0].text.value if messages.data else "{\"error\": \"No se pudo extraer información del texto.\"}"

        if raw_response.startswith("```json\n") and raw_response.endswith("\n```"):
            json_string = raw_response[8:-4]
        else:
            json_string = raw_response

        # Limpiar la cadena JSON
        json_string = json_string.replace('\xa0', ' ').strip()  # Reemplazar espacios duros y quitar espacios en blanco al principio y al final
        json_string = re.sub(r'[^\x00-\x7F]+', '', json_string) #Eliminar caracteres no ascii

        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}. Raw response: {raw_response}. Cleaned string: {json_string}")
            return {"error": f"La respuesta del asistente no es un JSON válido: {e}", "raw_response": raw_response, "cleaned_string": json_string}
        finally:
            openai.beta.assistants.delete(assistant.id)

    except Exception as e:
        print(f"Error al analizar texto: {e}")
        return {"error": str(e)}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS