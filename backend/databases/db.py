from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import urllib

# Cargar variables de entorno
load_dotenv()

# Leer datos de conexión desde .env
DB_USER = os.getenv("SQL_SERVER_USER")
DB_PASSWORD = os.getenv("SQL_SERVER_PASSWORD")
DB_HOST = os.getenv("SQL_SERVER_HOST")
DB_PORT = os.getenv("SQL_SERVER_PORT")
DB_NAME = os.getenv("SQL_SERVER_DBNAME")

print(f"Conectando a la base de datos {DB_NAME} en {DB_HOST}:{DB_PORT} como {DB_USER}")

# Construir la cadena de conexión ODBC
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={DB_HOST},{DB_PORT};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
    f"Encrypt=no;"
)

# URL codificada para SQLAlchemy
params = urllib.parse.quote_plus(connection_string)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Configuración de SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    # Función para inicializar las tablas
    def init_db():
        from databases.models.file_record import FileRecord
        from databases.models.invoice import InvoiceData
        from databases.models.log import LogData
        from databases import Base  # Asegúrate de que 'Base' esté definido y accesible

        Base.metadata.create_all(bind=engine)
        print("Tablas creadas")

except Exception as e:
    from modules.save_log import save_log

    log_action = "database_error"
    log_message = f"Error al configurar la base de datos: {e}"
    save_log(SessionLocal(), log_action, log_message)
    print(f"Error al configurar la base de datos: {e}")
    raise e