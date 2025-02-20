from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Leer datos de conexión desde .env
DB_USER = os.getenv("SQL_SERVER_USER")
DB_PASSWORD = os.getenv("SQL_SERVER_PASSWORD")
DB_HOST = os.getenv("SQL_SERVER_HOST")
DB_PORT = os.getenv("SQL_SERVER_PORT")
DB_NAME = os.getenv("SQL_SERVER_DBNAME")

try:
    # Configurar URL de conexión
    DATABASE_URL = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Configuración de SQLAlchemy
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Función para inicializar las tablas
    def init_db():
        from databases.models.file_record import FileRecord
        from databases.models.invoice import InvoiceData
        from databases.models.log import LogData

        Base.metadata.create_all(bind=engine)
        print("Tablas creadas")

except Exception as e:
    from modules.save_log import save_log

    log_action = "database_error"
    log_message = f"Error al configurar la base de datos: {e}"
    save_log(SessionLocal(), log_action, log_message)
    print(f"Error al configurar la base de datos: {e}")
    raise e
