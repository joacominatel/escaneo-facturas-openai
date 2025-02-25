import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_USER = os.getenv("SQL_SERVER_USER")
DB_PASSWORD = os.getenv("SQL_SERVER_PASSWORD")
DB_HOST = os.getenv("SQL_SERVER_HOST")
DB_PORT = os.getenv("SQL_SERVER_PORT")
DB_NAME = os.getenv("SQL_SERVER_DBNAME")

print(f"Conectando a la base de datos {DB_NAME} en {DB_HOST}:{DB_PORT} como {DB_USER}")
print(f"DB_PASSWORD: {DB_PASSWORD}")

# Construir la cadena de conexión sin Trusted_Connection (ya que usas usuario y contraseña)
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={DB_HOST},{DB_PORT};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
    f"Encrypt=no;"
)

try:
    conn = pyodbc.connect(connection_string)
    print("Conexión exitosa con pyodbc")
    conn.close()
except Exception as e:
    print("Error al conectar con pyodbc:", e)
