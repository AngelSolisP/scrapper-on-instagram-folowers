import subprocess
import time
import pyautogui
import os
import pandas as pd
import sqlite3


# Ruta al ejecutable de Chrome (ajústala según tu sistema)
chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

# URL de la extensión
extension_url = 'chrome-extension://kicgclkbiilobmccmmidfghnijgfamdb/options.html'

# Abrir Chrome con la URL de la extensión
subprocess.Popen([chrome_path, extension_url])

# Esperar a que Chrome se inicie
time.sleep(5)

# Coordenadas de los elementos (reemplaza con tus valores)
input_field_pos = (700, 616)
start_button_pos = (500, 908)
download_button_pos = (1218, 908)

# Interactuar con el campo de entrada
pyautogui.click(input_field_pos)
pyautogui.typewrite('https://www.instagram.com/caricakez/', interval=0.05)

# Hacer clic en el botón de iniciar
pyautogui.click(start_button_pos)

# Esperar a que el proceso termine
time.sleep(10)

# Hacer clic en el botón de descargar
pyautogui.click(download_button_pos)

time.sleep(2)

pyautogui.press('enter')

# Cerrar Chrome
#pyautogui.hotkey('alt', 'f4')

time.sleep(5)

# Esperar a que la descarga finalice
time.sleep(5)

# Ruta donde se guardará el archivo descargado
download_folder = 'C:\\Users\\angel\\Downloads'  # Ajusta esta ruta
downloaded_file = os.path.join(download_folder, 'caricakez_followers.csv')  # Ajusta el nombre del archivo

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
data = data[['userName', 'profileUrl', 'isVerified']]
print("Datos filtrados a las columnas: userName, profileUrl, isVerified.")

# Conectar a la base de datos SQLite
db_path = 'seguidores.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS seguidores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userName TEXT UNIQUE,
    profileUrl TEXT,
    isVerified INTEGER
)
''')
conn.commit()

# Insertar o actualizar datos
for index, row in data.iterrows():
    userName = row['userName']
    profileUrl = row['profileUrl']
    # Mapear 'Yes' a 1 y 'No' a 0
    isVerified = 1 if str(row['isVerified']).strip().lower() == 'yes' else 0

    cursor.execute('''
    INSERT OR REPLACE INTO seguidores (userName, profileUrl, isVerified)
    VALUES (?, ?, ?)
    ''', (userName, profileUrl, isVerified))

conn.commit()
conn.close()

# Cerrar Chrome
#pyautogui.hotkey('alt', 'f4')
