import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Configuración de la página de Streamlit
st.set_page_config(page_title='Análisis de Seguidores', layout='wide')

# Conectar a la base de datos
db_path = 'seguidores.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Leer las tablas
seguidores_df = pd.read_sql_query("SELECT * FROM seguidores", conn)
hourly_stats_df = pd.read_sql_query("SELECT * FROM hourly_stats ORDER BY timestamp", conn)

conn.close()

# Convertir 'timestamp' a tipo datetime
hourly_stats_df['timestamp'] = pd.to_datetime(hourly_stats_df['timestamp'])

# Filtrar datos a los últimos 10 días y próximos 10 días
current_time = datetime.now()
start_time = current_time - timedelta(days=10)
end_time = current_time + timedelta(days=10)

filtered_stats_df = hourly_stats_df[
    (hourly_stats_df['timestamp'] >= start_time) &
    (hourly_stats_df['timestamp'] <= end_time)
].copy()

# Mostrar estadísticas generales
st.title('Análisis de Seguidores')

st.header('Estadísticas Generales')

total_seguidores = len(seguidores_df)
verificados = seguidores_df['isVerified'].sum()
porcentaje_verificados = (verificados / total_seguidores) * 100 if total_seguidores > 0 else 0

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Total de Seguidores", value=total_seguidores)

with col2:
    st.metric(label="Seguidores Verificados", value=f"{verificados} ({porcentaje_verificados:.2f}%)")

# Gráfica de nuevos seguidores por hora
st.header('Crecimiento Horario de Nuevos Seguidores')

fig1, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(filtered_stats_df['timestamp'], filtered_stats_df['new_followers'], marker='o', linestyle='-')
ax1.set_xlabel('Fecha y Hora')
ax1.set_ylabel('Nuevos Seguidores')
ax1.set_title('Crecimiento Horario de Nuevos Seguidores')
ax1.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig1)

# Gráfica del total acumulado de seguidores
st.header('Crecimiento Acumulado de Seguidores')

# Calcular el total acumulado basado en hourly_stats_df dentro el rango filtrado
filtered_stats_df = filtered_stats_df.sort_values('timestamp')
filtered_stats_df['total_followers'] = filtered_stats_df['new_followers'].cumsum()

fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.plot(filtered_stats_df['timestamp'], filtered_stats_df['total_followers'], marker='o', linestyle='-')
ax2.set_xlabel('Fecha y Hora')
ax2.set_ylabel('Total Acumulado de Seguidores')
ax2.set_title('Crecimiento Acumulado de Seguidores')
ax2.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2)

# Gráfica de seguidores verificados vs no verificados
st.header('Distribución de Seguidores Verificados')

fig3, ax3 = plt.subplots(figsize=(6, 6))
labels = ['Verificados', 'No Verificados']
sizes = [verificados, total_seguidores - verificados]
colors = ['gold', 'lightcoral']
explode = (0.1, 0)  # Resaltar la primera porción

ax3.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)

ax3.axis('equal')  # Igualar ejes para que el pastel sea circular
ax3.set_title('Distribución de Seguidores Verificados')
st.pyplot(fig3)

# Mostrar tabla de seguidores con opciones de filtrado
st.header('Listado de Seguidores')

# Opciones de filtrado
filter_option = st.selectbox("Filtrar por verificación:", ["Todos", "Verificados", "No Verificados"])

if filter_option == "Verificados":
    filtered_df = seguidores_df[seguidores_df['isVerified'] == 1]
elif filter_option == "No Verificados":
    filtered_df = seguidores_df[seguidores_df['isVerified'] == 0]
else:
    filtered_df = seguidores_df

# Filtrar la tabla de seguidores a los últimos 10 días y próximos 10 días
filtered_df['date_added'] = pd.to_datetime(filtered_df['date_added'])
filtered_df = filtered_df[
    (filtered_df['date_added'] >= start_time) &
    (filtered_df['date_added'] <= end_time)
]

st.dataframe(filtered_df[['userName', 'profileUrl', 'isVerified', 'date_added', 'date_last_seen']].sort_values(by='date_added', ascending=False))
