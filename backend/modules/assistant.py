from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import threading

# Cargar variables de entorno
load_dotenv()
client = OpenAI()

# Crear texto de la factura
# pdf_text = extract_text_from_scanned_pdf("./facturas/Transaction_238462118.pdf")
# print(pdf_text)
invoice = "./facturas/Transaction_238383815.pdf"

# Crear archivo en OpenAI
file = client.files.create(
    file=open(invoice, "rb"),
    purpose="assistants",
)

# Crear hilo y mensaje inicial
default_message = "Extract the invoice data from the provided text or attachment."

def create_thread_with_file(file_id, content=default_message):
  return client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": content,
        "attachments": [
          {
            "file_id": file_id,
            "tools": [{"type": "code_interpreter"}]
          }
        ]
      }
    ]
  )

thread = create_thread_with_file(file.id)

def run_assistant(thread_id, assistant_id, instructions):
  return client.beta.threads.runs.create_and_poll(
    thread_id=thread_id,
    assistant_id=assistant_id,
    instructions=instructions,
  )

# Ejecutar el asistente
run = run_assistant(
  thread.id, 
  os.getenv("ASSISTANT_ID"), 
  "Extract the invoice data from the provided text or attachment. Include items"
  )

progress_status = ["queued", "in_progress", "cancelling"]
final_status = ["completed", "failed", "cancelled"]
other_status = ["requires_action", "expired", "incomplete"]

def track_status(run_id):
  while True:
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run_id)
    print(f"Run status: {run.status}")
    
    if run.status in final_status:
      if run.status == "completed":
        print("Run completed successfully.")
      elif run.status == "failed":
        print(f"Run failed: {run.last_error}")
      else:
        print(f"Run ended with status: {run.status}")
      break
    elif run.status in other_status:
      print(f"Run status: {run.status}")
      break
    else:
      print("\rWaiting for the run to complete...", end="")
    
    time.sleep(5)

def fetch_results(thread_id):
  try:
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages.data:
      for content_block in msg.content:
        value = content_block.text.value
        if value:
          print(value)
    print("\n\n\n\n\n" + messages)
  except Exception as e:
    print(f"Error: {e}")

# Start tracking the status in a separate thread
status_thread = threading.Thread(target=track_status, args=(run.id,))
status_thread.start()

# Wait for the status tracking thread to finish
status_thread.join()

# Fetch and print the results
fetch_results(thread.id)