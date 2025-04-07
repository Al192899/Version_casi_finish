import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd

# 1. Crear base de datos y tablas
def create_db():
    """Crea las tablas 'loads' y 'pallets' en la base de datos si no existen."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    cursor = conn.cursor()

    # Crear tabla de loads
    cursor.execute('''CREATE TABLE IF NOT EXISTS loads (
        Load TEXT PRIMARY KEY,
        Trailer TEXT NOT NULL,
        Rampa TEXT NOT NULL,
        Destino TEXT NOT NULL,
        Fecha TEXT NOT NULL,
        Cantidad_Pallets INTEGER NOT NULL
    )''')

    # Crear tabla de pallets con clave compuesta
    cursor.execute('''CREATE TABLE IF NOT EXISTS pallets (
        PalletID TEXT NOT NULL,
        Load TEXT NOT NULL,
        FechaEscaneo TEXT,
        PRIMARY KEY (PalletID, Load),
        FOREIGN KEY (Load) REFERENCES loads (Load)
    )''')

    conn.commit()
    conn.close()
    print("\u2705 Tablas 'loads' y 'pallets' creadas correctamente.")

# 2. Registrar un Load
def register_load(load, trailer, rampa, destino, cantidad_pallets):
    """Registra un nuevo Load en la base de datos, sin insertar pallets aún."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    try:
        cursor = conn.cursor()

        # Verificar si el Load ya está registrado
        cursor.execute("SELECT COUNT(*) FROM loads WHERE Load = ?", (load,))
        exists = cursor.fetchone()[0]

        if exists > 0:
            print(f"\u26a0\ufe0f El Load '{load}' ya está registrado.")
            return

        # Registrar el Load
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''INSERT INTO loads (Load, Trailer, Rampa, Destino, Fecha, Cantidad_Pallets)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (load, trailer, rampa, destino, fecha_actual, cantidad_pallets))

        # Ya no insertamos los pallets aquí. Se agregarán al escanear.
        conn.commit()
        print(f"\u2705 Load '{load}' registrado con {cantidad_pallets} pallets esperados.")
    except Exception as e:
        print(f"Error al registrar el Load: {e}")
    finally:
        conn.close()

# 3. Agregar un pallet manualmente
def add_package(pallet_code, load):
    """Agrega un pallet específico a la base de datos."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pallets (PalletID, Load, FechaEscaneo) VALUES (?, ?, ?)', 
                       (pallet_code, load, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        print(f"\u2705 Pallet '{pallet_code}' agregado correctamente al Load '{load}'")
    except sqlite3.IntegrityError as e:
        print(f"Error al agregar el pallet: {e}")
    finally:
        conn.close()

# 4. Escanear un pallet
def scan_pallet(load, pallet_id):
    """Marca un pallet como escaneado dentro de un Load específico."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    try:
        cursor = conn.cursor()

        # Verificar si el pallet ya fue escaneado
        cursor.execute('SELECT COUNT(*) FROM pallets WHERE PalletID = ? AND Load = ?', (pallet_id, load))
        exists = cursor.fetchone()[0]

        if exists > 0:
            print(f"\u26a0\ufe0f El pallet '{pallet_id}' ya fue escaneado anteriormente para el Load '{load}'.")
        else:
            cursor.execute('INSERT INTO pallets (PalletID, Load, FechaEscaneo) VALUES (?, ?, ?)',
                           (pallet_id, load, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            print(f"\u2705 Pallet '{pallet_id}' escaneado exitosamente en el Load '{load}'.")
    except Exception as e:
        print(f"Error al escanear el pallet: {e}")
    finally:
        conn.close()

# 5. Obtener todos los pallets
def get_all_packages(load=None):
    """Obtiene todos los pallets de un Load específico o de todos los Loads."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    cursor = conn.cursor()

    if load:
        cursor.execute("SELECT PalletID, FechaEscaneo FROM pallets WHERE Load = ?", (load,))
    else:
        cursor.execute("SELECT PalletID, Load, FechaEscaneo FROM pallets")

    results = cursor.fetchall()
    conn.close()

    if not results:
        print("\u274c No se encontraron pallets.")
        return []

    # Convierte los resultados en cadenas para evitar errores
    formatted_results = [", ".join(map(str, row)) for row in results]
    return formatted_results

# 6. Verificar si un Load es único
def is_load_unique(load):
    """Verifica si un Load es único en la base de datos."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM loads WHERE Load = ?", (load,))
    exists = cursor.fetchone()[0]
    conn.close()
    return exists == 0  # True si es único

# 7. Exportar datos a Excel
def export_to_excel():
    """Exporta los datos de loads y pallets a un archivo de Excel."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    cursor = conn.cursor()

    cursor.execute('''SELECT l.Load, l.Trailer, l.Rampa, l.Destino, l.Fecha, l.Cantidad_Pallets, p.PalletID
                      FROM loads l
                      LEFT JOIN pallets p ON l.Load = p.Load
                      ORDER BY l.Load, p.PalletID''')

    rows = cursor.fetchall()
    conn.close()

    # Convierte cada valor en cadena para evitar problemas
    formatted_rows = [tuple(map(str, row)) for row in rows]

    columns = ["Load", "Trailer", "Rampa", "Destino", "Fecha", "Cantidad de Pallets", "PalletID"]
    df = pd.DataFrame(formatted_rows, columns=columns)
    df.to_excel("loads_and_pallets_data.xlsx", index=False, engine='openpyxl')
    print("\u2705 Datos exportados a 'loads_and_pallets_data.xlsx' exitosamente.")

# 8. Generar reporte PDF
def generate_pdf():
    """Genera un reporte PDF de todos los loads y sus pallets asociados."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    cursor = conn.cursor()

    cursor.execute('''SELECT l.Load, l.Trailer, l.Rampa, l.Destino, l.Fecha, l.Cantidad_PalletS, p.PalletID
                      FROM loads l
                      LEFT JOIN pallets p ON l.Load = p.Load
                      ORDER BY l.Load, p.PalletID''')

    rows = cursor.fetchall()
    conn.close()

    pdf_file = "loads_and_pallets_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Reporte de Loads y Pallets")

    x, y = 50, 700
    for row in rows:
        # Convierte cada elemento de la fila en cadena para evitar errores
        formatted_row = ", ".join(map(str, row))
        c.drawString(x, y, formatted_row)
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750

    c.save()
    print(f"\u2705 PDF generado exitosamente: {pdf_file}")

# 9. Obtener el número esperado de pallets para un Load
def get_expected_pallet_count(load):
    """Obtiene el número esperado de pallets para un Load específico."""
    conn = sqlite3.connect('routing(loads-in-charge-region).db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT Cantidad_Pallets FROM loads WHERE Load = ?", (load,))
        result = cursor.fetchone()
        
        if result:
            return result[0]  # Devuelve el número de pallets esperado para el Load
        else:
            print(f"\u26a0\ufe0f El Load '{load}' no existe.")
            return 0  # Retorna 0 si no se encuentra el Load

    except Exception as e:
        print(f"Error al obtener el número de pallets esperados: {e}")
        return 0  # En caso de error, retornamos 0
    finally:
        conn.close()
