import os
import glob
import time
import threading
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
client = OpenAI()

# Variables globales
DEFAULT_MESSAGE = "Extract the invoice data from the provided text or attachment."
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
FINAL_STATUSES = ["completed", "failed", "cancelled"]
OTHER_STATUSES = ["requires_action", "expired", "incomplete"]

def load_invoices(directory_path):
    """Carga las facturas desde un directorio especificado."""
    return glob.glob(os.path.join(directory_path, "*"))

def create_file_in_openai(file_path):
    """Sube un archivo a OpenAI y lo asocia a un propósito."""
    try:
        with open(file_path, "rb") as file:
            response = client.files.create(file=file, purpose="assistants")
        return response.id
    except Exception as e:
        print(f"Error uploading file {file_path}: {e}")
        return None

def create_thread_with_file(file_id, message=DEFAULT_MESSAGE):
    """Crea un hilo con un archivo asociado."""
    try:
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                    "attachments": [
                        {"file_id": file_id, "tools": [{"type": "code_interpreter"}]}
                    ],
                }
            ]
        )
        return thread.id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None

def run_assistant(thread_id, assistant_id, instructions):
    """Ejecuta el asistente para procesar el hilo."""
    try:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=instructions,
        )
        return run.id
    except Exception as e:
        print(f"Error running assistant: {e}")
        return None

def track_status(thread_id, run_id):
    """Realiza un seguimiento del estado del procesamiento."""
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            print(f"Run status: {run.status}")
            
            if run.status in FINAL_STATUSES:
                if run.status == "completed":
                    print("Run completed successfully.")
                elif run.status == "failed":
                    print(f"Run failed: {run.last_error}")
                    return "error"
                else:
                    print(f"Run ended with status: {run.status}")
                return run.status
            elif run.status in OTHER_STATUSES:
                print(f"Run requires action or is incomplete: {run.status}")
                return run.status
            else:
                print("\rWaiting for the run to complete...", end="")
            
            time.sleep(5)
        except Exception as e:
            print(f"Error tracking status: {e}")
            return "error"

def fetch_results(thread_id):
    """Obtiene y devuelve los resultados del procesamiento."""
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        # print(f"Messages: {messages.data}")
        extracted_data = []
        for msg in messages.data:
            for content_block in msg.content:
                value = content_block.text.value
                if value:
                    extracted_data.append(value)
        return extracted_data
    except Exception as e:
        print(f"Error fetching results: {e}")
        return []

def process_invoices(directory_path):
    """Procesa todas las facturas en el directorio especificado."""
    invoices = load_invoices(directory_path)
    if not invoices:
        print("No invoices found.")
        return

    results = []
    for invoice_path in invoices:
        print(f"Processing file: {invoice_path}")
        file_id = create_file_in_openai(invoice_path)
        if not file_id:
            continue

        thread_id = create_thread_with_file(file_id)
        if not thread_id:
            continue

        run_id = run_assistant(thread_id, ASSISTANT_ID, DEFAULT_MESSAGE)
        if not run_id:
            continue

        # Track status in a separate thread
        status = track_status(thread_id, run_id)
        if status == "completed":
            data = fetch_results(thread_id)
            results.append({"file": invoice_path, "data": data})
        else:
            results.append({"file": invoice_path, "error": f"Status: {status}"})
    
    return results

def assistant_process_invoices(file_path, question):
    """
    Process an invoice file and extract data using OpenAI API.
    :param file_path: Path to the file to process
    :param question: Question or instructions for processing
    :return: Extracted data
    """
    try:
        file_id = create_file_in_openai(file_path)
        if not file_id:
            return "Error uploading file to OpenAI"

        thread_id = create_thread_with_file(file_id, question)
        if not thread_id:
            return "Error creating thread in OpenAI"

        run_id = run_assistant(thread_id, ASSISTANT_ID, question)
        if not run_id:
            return "Error running assistant in OpenAI"

        # Track status in a separate thread
        status = track_status(thread_id, run_id)
        if status == "completed":
            return fetch_results(thread_id)
        else:
            return f"Processing status: {status}"
    except Exception as e:
        return f"Error processing file: {e}"

if __name__ == "__main__":
    # Define el directorio de las facturas
    INVOICE_DIR = "facturas/"
    
    # Procesa todas las facturas en el directorio
    processed_data = process_invoices(INVOICE_DIR)

    # Muestra los resultados
    try:
        for result in processed_data:
            if "error" in result:
                print(f"Error processing file {result['file']}: {result['error']}")
            else:
                print(f"Processed file: {result['file']}")
                for data in result["data"]:
                    print(data)
    except Exception as e:
        print(f"Error displaying results: {e}")