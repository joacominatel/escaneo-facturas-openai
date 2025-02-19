global INSTRUCTIONS

INSTRUCTIONS = f"""
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
                - **Advertising Number (OP numbers)**: Extrae cualquier número de operación que comience con "OP". Estos pueden ser números independientes (ej., "OP123456") o múltiples entradas. Si no se encuentra ningún número de operación, este campo debe omitirse para ese artículo.
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
                        "advertising_number": []
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