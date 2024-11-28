from openai import OpenAI
from dotenv import load_dotenv
import os
from pdf2image import convert_from_path
# Cargar variables de entorno
load_dotenv()
client = OpenAI()

# Crear texto de la factura
# pdf_text = extract_text_from_scanned_pdf("./facturas/Transaction_238462118.pdf")
# print(pdf_text)
invoice = convert_from_path("./facturas/Transaction_238462118.pdf")
# save the image as a jpeg file
invoice[0].save('facturas/Transaction_238462118.jpg')
invoice = 'facturas/Transaction_238462118.jpg'
# Crear archivo en OpenAI
file = client.files.create(
    file=open(invoice, "rb"),
    purpose="assistants",
)

# Crear hilo y mensaje inicial
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "Extract the invoice data from the provided text or attachment.",
      "attachments": [
        {
          "file_id": file.id,
          "tools": [{"type": "code_interpreter"}]
        }
      ]
    }
  ]
)


run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=os.getenv("ASSISTANT_ID"),
    instructions="Extract the invoice data from the provided text or attachment.",
)

    # print(message.data[1].content[0].text.value)
if run.status == "completed":
    try:
        # Obtener los mensajes del hilo
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print("Assistant run succeeded. Response:")
        
        # Extraer y mostrar solo el contenido relevante
        for msg in messages.data:
            for content_block in msg.content:
                value = content_block.text.value
                if value:
                    print(value)
    except Exception as e:
        print(f"An error occurred while retrieving messages: {e}")
else:
    print("Assistant run failed. Response:")
    print(run)