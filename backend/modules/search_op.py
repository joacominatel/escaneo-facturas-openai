from sqlalchemy import func
from sqlalchemy.dialects.mssql import JSON
from databases.models.invoice import InvoiceData

def search_invoices_by_advertising_order(session, advertising_number, offset=0, limit=10):
    """
    Busca facturas que contengan el advertising_order especificado dentro de sus items.

    Args:
        session: Objeto de sesión de SQLAlchemy.
        advertising_number: El número de operación a buscar.
        offset: El número de resultados a omitir (para paginación).
        limit: El número máximo de resultados a devolver.

    Returns:
        Una tupla que contiene:
            - Una lista de objetos InvoiceData que contienen el número de operación coincidente.
            - El total de resultados coincidentes (sin aplicar limit u offset).
    """

    # Subconsulta para obtener los ids que coinciden con la búsqueda
    subquery = session.query(InvoiceData.id) \
        .filter(func.json_contains(InvoiceData.items.cast(JSON), advertising_number)).subquery()

    # Consulta principal usando la subconsulta
    query = session.query(InvoiceData).filter(InvoiceData.id.in_(subquery))

    total = query.count() # Obtener el total de resultados antes de aplicar limit y offset

    results = query.offset(offset).limit(limit).all()

    return results, total