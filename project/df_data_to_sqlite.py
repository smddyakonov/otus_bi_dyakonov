import pandas as pd
import sqlite3

# Шаг 1: Загрузка файла Excel в DataFrame
file_path = 'df_data_ee.xlsx'  # Укажите путь к вашему файлу Excel
df = pd.read_excel(file_path)

# Шаг 2: Создание базы данных SQLite и сохранение данных
conn = sqlite3.connect('data.db')  # Имя базы данных SQLite
df.to_sql('df_data_ee', conn, if_exists='replace', index=False)

# Закрытие соединения с базой данных
conn.close()

print("Данные успешно сохранены в SQLite!")