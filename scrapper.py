import subprocess
import time
import pyautogui
import os
import pandas as pd
import sqlite3
import datetime

# ---------------------------
# Configuración Inicial
# ---------------------------

# Ruta al ejecutable de Chrome (ajústala según tu sistema)
chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

# URL de la extensión o página desde donde descargar el CSV
extension_url = 'chrome-extension://kicgclkbiilobmccmmidfghnijgfamdb/options.html'  # Reemplaza con tu URL real

# Ruta donde se guardará el archivo descargado
download_folder = 'C:\\Users\\angel\\Downloads'  # Ajusta esta ruta
downloaded_file = os.path.join(download_folder, 'caricakez_followers.csv')  # Ajusta el nombre del archivo

# Coordenadas de los elementos (reemplaza con tus valores)
input_field_pos = (700, 616)        # Posición del campo de entrada
start_button_pos = (500, 908)       # Posición del botón de iniciar
download_button_pos = (1218, 908)   # Posición del botón de descargar

# ---------------------------
# Función para Añadir Columnas
# ---------------------------

def add_column_if_not_exists(cursor, table_name, column_name, column_type):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"Columna '{column_name}' añadida a la tabla '{table_name}'.")
        conn.commit()

# ---------------------------
# Automatización de la Descarga
# ---------------------------

# Abrir Chrome con la URL de la extensión
subprocess.Popen([chrome_path, extension_url])

# Esperar a que Chrome se inicie
time.sleep(5)

# Interactuar con el campo de entrada
pyautogui.click(input_field_pos)
pyautogui.typewrite('https://www.instagram.com/caricakez/', interval=0.05)  # Reemplaza con tu URL real

# Hacer clic en el botón de iniciar
pyautogui.click(start_button_pos)

# Esperar a que el proceso termine (ajusta el tiempo según sea necesario)
time.sleep(10)

# Hacer clic en el botón de descargar
pyautogui.click(download_button_pos)

time.sleep(2)

# Presionar "Enter" para confirmar la descarga (si aparece el diálogo)
pyautogui.press('enter')

# Cerrar Chrome (descomenta si deseas cerrar Chrome automáticamente)
# pyautogui.hotkey('alt', 'f4')

# Esperar a que la descarga finalice
time.sleep(10)

# ---------------------------
# Verificar Descarga del Archivo
# ---------------------------

# Esperar hasta que el archivo exista
wait_time = 0
while not os.path.exists(downloaded_file) and wait_time < 60:
    time.sleep(1)
    wait_time += 1

if os.path.exists(downloaded_file):
    print("Archivo descargado correctamente.")
else:
    print("No se pudo encontrar el archivo descargado.")
    exit()

# ---------------------------
# Leer y Procesar el Archivo CSV
# ---------------------------

# Leer el archivo CSV
try:
    data = pd.read_csv(downloaded_file)
    print("Datos leídos exitosamente.")
except Exception as e:
    print(f"Error al leer el archivo CSV: {e}")
    exit()

# Mostrar las columnas disponibles (opcional)
print("Columnas disponibles en el CSV:", data.columns.tolist())

# Seleccionar solo las columnas deseadas
# Asegúrate de que estos nombres de columna coincidan con los de tu archivo CSV
try:
    data = data[['userName', 'profileUrl', 'isVerified']]
    print("Datos filtrados a las columnas: userName, profileUrl, isVerified.")
except KeyError as e:
    print(f"Error: La columna {e} no existe en el CSV.")
    exit()

# Limitar a los primeros 500 seguidores si es necesario
data = data.head(500)

# ---------------------------
# Obtener Fecha y Hora Actual (Redondeada a la Hora)
# ---------------------------

current_datetime = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
current_date_str = current_datetime.strftime('%Y-%m-%d')
current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

# ---------------------------
# Conectar a la Base de Datos SQLite
# ---------------------------

db_path = 'seguidores.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla 'seguidores' si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS seguidores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userName TEXT UNIQUE,
    profileUrl TEXT,
    isVerified INTEGER
)
''')
conn.commit()

# Añadir las columnas 'date_added' y 'date_last_seen' si no existen
add_column_if_not_exists(cursor, 'seguidores', 'date_added', 'TEXT')
add_column_if_not_exists(cursor, 'seguidores', 'date_last_seen', 'TEXT')

# Crear la tabla 'hourly_stats' para estadísticas horarias si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS hourly_stats (
    timestamp TEXT PRIMARY KEY,
    new_followers INTEGER
)
''')
conn.commit()

# Insertar o actualizar datos
new_followers_count = 0

for index, row in data.iterrows():
    userName = row['userName']
    profileUrl = row['profileUrl']
    # Mapear 'Yes' a 1 y 'No' a 0
    isVerified = 1 if str(row['isVerified']).strip().lower() == 'yes' else 0

    # Verificar si el seguidor ya existe
    cursor.execute('SELECT * FROM seguidores WHERE userName = ?', (userName,))
    result = cursor.fetchone()

    if result:
        # El seguidor ya existe, actualizamos 'date_last_seen'
        cursor.execute('''
        UPDATE seguidores
        SET profileUrl = ?, isVerified = ?, date_last_seen = ?
        WHERE userName = ?
        ''', (profileUrl, isVerified, current_datetime_str, userName))
    else:
        # Nuevo seguidor, insertamos y contamos
        cursor.execute('''
        INSERT INTO seguidores (userName, profileUrl, isVerified, date_added, date_last_seen)
        VALUES (?, ?, ?, ?, ?)
        ''', (userName, profileUrl, isVerified, current_datetime_str, current_datetime_str))
        new_followers_count += 1

conn.commit()

# Actualizar las estadísticas horarias
cursor.execute('SELECT new_followers FROM hourly_stats WHERE timestamp = ?', (current_datetime_str,))
result = cursor.fetchone()

if result:
    # Si ya existe, sumamos el conteo actual
    total_new_followers = result[0] + new_followers_count
    cursor.execute('''
    UPDATE hourly_stats
    SET new_followers = ?
    WHERE timestamp = ?
    ''', (total_new_followers, current_datetime_str))
else:
    # Si no existe, insertamos el registro para la hora
    total_new_followers = new_followers_count
    cursor.execute('''
    INSERT INTO hourly_stats (timestamp, new_followers)
    VALUES (?, ?)
    ''', (current_datetime_str, total_new_followers))

conn.commit()
conn.close()

print(f"Nuevos seguidores detectados en esta descarga: {new_followers_count}")
print(f"Total de nuevos seguidores en esta hora ({current_datetime_str}): {total_new_followers}")
