from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Leer datos de conexión desde .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

try:
    # Configurar URL de conexión
    DATABASE_URL = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Configuración de SQLAlchemy
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Función para inicializar las tablas
    def init_db():
        from databases.models.file_record import FileRecord  # Importar modelo
        from databases.models.invoice import InvoiceData
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas")

except Exception as e:
    print(f"Error al configurar la base de datos: {e}")
    raise
