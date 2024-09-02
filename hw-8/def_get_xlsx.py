import pandas as pd
from pathlib import Path

def get_xlsx(file, path=None, parse_flag=False, sheet_name=None, header_row = None):
    """
    Получение информации о файле Excel.

    Параметры:
    - file (str): Имя файла Excel.
    - path (str, необязательно): Путь к папке, содержащей файл Excel.
    Если не указан, предполагается, что в переменную file передан абсолютный путь к файлу или файл находится в тойже папке что и notebook.
    - parse_flag (bool, необязательно): Если True, распарсить файл Excel и вернуть указанный лист в виде DataFrame.
    Если False, вывести имя файла и имена листов.
    - sheet_name (str, необязательно): Имя листа для парсинга, если parse_flag равен True
    - header_row (int, необязательно): Номер строки, с которой прочитать лист sheet_name.

    Возвращает:
    - None: Если parse_flag равен False, функция выводит имя файла и имена листов.
    - pd.DataFrame: Если parse_flag равен True, функция возвращает указанный лист в виде pandas DataFrame.

    Пример:
    ```
    # Вывести имя файла и имена листов
    get_xlsx("пример.xlsx")

    # Распарсить определенный лист и вернуть в виде DataFrame
    df = get_xlsx("пример.xlsx", parse_flag=True, sheet_name="Лист1")
    ```
    Код функции
    import pandas as pd
    from pathlib import Path

    # Сформировать полный путь к файлу Excel
    if path is None:
        file = Path(Path.cwd(), file)  # Файл в текущей рабочей директории или задан абсолютный путь
    else:
        file = Path(path, file)  # Файл в указанной директории

    xl = pd.ExcelFile(file)

    if not parse_flag:
        # Вывести имя файла и имена листов
        print(file)
        print(xl.sheet_names)
    else:
        # Распарсить указанный лист и вернуть в виде DataFrame
        df = xl.parse(sheet_name, header=header_row)
        return df

    """

    # Сформировать полный путь к файлу Excel
    if path is None:
        file = Path(Path.cwd(), file)  # Файл в текущей рабочей директории или задан абсолютный путь
    else:
        file = Path(path, file)  # Файл в указанной директории

    xl = pd.ExcelFile(file)

    if not parse_flag:
        # Вывести имя файла и имена листов
        print(file)
        print(xl.sheet_names)
    else:
        # Распарсить указанный лист и вернуть в виде DataFrame
        df = xl.parse(sheet_name, header=header_row)
        return df