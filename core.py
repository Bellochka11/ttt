import json


from utils import save_table_data, load_table_data
from src.decorators import handle_db_errors, confirm_action, log_time, create_cacher


SUPPORTED_DATA_TYPES = {'int', 'str', 'bool'}
METADATA = "db_meta.json"

cache_result = create_cacher()

@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу с указанными столбцами."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None
    new_columns = {"ID": "int"}
    for column in columns:
        if ":" not in column:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        name, type_ = column.split(":", 1)
        if not name or type_ not in SUPPORTED_DATA_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        if any(existing.lower() == name.lower() for existing in new_columns):
            print(f"Некорректное значение: {name}. Попробуйте снова.")
            return None
        new_columns[name] = type_
    metadata[table_name] = new_columns
    columns_info = ", ".join(
        f"{name}:{type_}" for name, type_ in new_columns.items()
    )
    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_info}"
    )
    return metadata

@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

@handle_db_errors
def list_tables(metadata):
    """Выводит список существующих таблиц."""
    if not metadata:
        print("Таблиц нет.")
        return
    for table_name in metadata:
        print(f"- {table_name}")

@log_time
@handle_db_errors
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    columns = metadata[table_name]
    user_columns = list(columns.keys())[1:]
    user_types = list(columns.values())[1:]
    if len(values) != len(user_columns):
        print('Количество переданных значений не соответствует количеству столбцов!')
        return
    data = load_table_data(table_name)
    new_id = len(data) + 1
    new_row = {"id": new_id}
    for column, value, type_ in zip(user_columns, values, user_types):
        if type_ == "int" and type(value) is not int:
            print(f'Ошибка: "{column}" должен быть int.')
            return
        if type_ == "str" and type(value) is not str:
            print(f'Ошибка: "{column}" должен быть str.')
            return
        if type_ == "bool" and type(value) is not bool:
            print(f'Ошибка: "{column}" должен быть bool.')
            return
        new_row[column] = value
    data.append(new_row)
    save_table_data(table_name, data)
    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )
    return data


@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    """Возвращает записи таблицы с учётом условия фильтрации."""
    key = json.dumps(
        {
            "data": table_data,
            "where": where_clause,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    def get_rows():
        if where_clause is None:
            return table_data
        return [
            row
            for row in table_data
            if all(
                row.get(column) == value
                for column, value in where_clause.items()
            )
        ]
    return cache_result(key, get_rows)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет значения в записях, соответствующих условию."""
    for row in table_data:
        matches = True
        for column, value in where_clause.items():
            if row.get(column) != value:
                matches = False
                break
        if matches:
            row.update(set_clause)
    return table_data



@confirm_action("удаление записей")
@handle_db_errors
def delete(table_data, where_clause):
    """Удаляет записи, соответствующие условию."""
    result = []
    for row in table_data:
        matches = True
        for column, value in where_clause.items():
            if row.get(column) != value:
                matches = False
                break
        if not matches:
            result.append(row)
    return result



@handle_db_errors
def info(metadata, table_name, table_data):
    """Выводит информацию о таблице и количестве записей."""
    if table_name not in metadata:
        print(f'Таблица "{table_name}" не существует.')
        return
    columns = metadata[table_name]
    columns_info = ", ".join(
        f"{column}:{data_type}"
        for column, data_type in columns.items()
    )
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_info}")
    print(f"Количество записей: {len(table_data)}")
