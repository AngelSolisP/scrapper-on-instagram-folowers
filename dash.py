import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Conectar a la base de datos
db_path = 'seguidores.db'
conn = sqlite3.connect(db_path)

# Leer las tablas
seguidores_df = pd.read_sql_query("SELECT * FROM seguidores", conn)
daily_stats_df = pd.read_sql_query("SELECT * FROM daily_stats ORDER BY date", conn)

conn.close()

# Mostrar estadísticas generales
total_seguidores = len(seguidores_df)
verificados = seguidores_df['isVerified'].sum()
porcentaje_verificados = (verificados / total_seguidores) * 100 if total_seguidores > 0 else 0

print(f"Total de seguidores: {total_seguidores}")
print(f"Seguidores verificados: {verificados} ({porcentaje_verificados:.2f}%)")

# Convertir la columna 'date' a tipo fecha
daily_stats_df['date'] = pd.to_datetime(daily_stats_df['date'])

# Gráfica del crecimiento diario de nuevos seguidores
plt.figure(figsize=(10, 6))
plt.plot(daily_stats_df['date'], daily_stats_df['new_followers'], marker='o', linestyle='-')
plt.xlabel('Fecha')
plt.ylabel('Nuevos Seguidores')
plt.title('Crecimiento Diario de Nuevos Seguidores')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Calcular el total acumulado
daily_stats_df['total_followers'] = daily_stats_df['new_followers'].cumsum()

# Gráfica del total acumulado de seguidores
plt.figure(figsize=(10, 6))
plt.plot(daily_stats_df['date'], daily_stats_df['total_followers'], marker='o', linestyle='-')
plt.xlabel('Fecha')
plt.ylabel('Total Acumulado de Seguidores')
plt.title('Crecimiento Acumulado de Seguidores')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Gráfica de seguidores verificados vs no verificados
plt.figure(figsize=(6, 6))
labels = ['Verificados', 'No Verificados']
sizes = [verificados, total_seguidores - verificados]
colors = ['gold', 'lightcoral']
explode = (0.1, 0)  # Resaltar la primera porción

plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)

plt.axis('equal')  # Igualar ejes para que el pastel sea circular
plt.title('Distribución de Seguidores Verificados')
plt.show()
