import pandas as pd
import sqlite3


def load_data_from_sqlite(db_path, table_name):
    """
    Загружает данные из таблицы SQLite в Pandas DataFrame.

    :param db_path: Путь к файлу базы данных SQLite.
    :param table_name: Имя таблицы, из которой нужно загрузить данные.
    :return: Pandas DataFrame с данными из указанной таблицы.
    """
    # Подключение к базе данных SQLite
    conn = sqlite3.connect(db_path)

    # Загрузка данных из таблицы в DataFrame
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)

    # Закрытие соединения с базой данных
    conn.close()

    return df

#db_path = 'data.db'        # Укажите путь к вашему файлу базы данных SQLite
#table_name = 'df_data_ee'  # Укажите имя таблицы

#df = load_data_from_sqlite(db_path, table_name)
#print(df.info())

