import prompt, shlex


from parser import parse_insert, parse_select, parse_update, parse_delete
from utils import save_metadata, save_table_data
from core import create_table, drop_table, list_tables, insert, select, update, delete, info
from utils import load_metadata, load_table_data

METADATA = "db_meta.json"
TABLE_DATA = "data/users.json"

def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

# def print_table(metadata, table_name, rows):
#     columns = metadata[table_name]

#     table = PrettyTable()
#     table.field_names = [
#         name.upper() if name == "id" else name
#         for name in columns
#     ]

#     for row in rows:
#         table.add_row([row.get(name) for name in columns])

#     print(table)


# def print_info(metadata, table_name):
#     if table_name not in metadata:
#         print(f'Ошибка: Таблица "{table_name}" не существует.')
#         return

#     data = load_table_data(table_name)
#     columns = metadata[table_name]

#     structure = ", ".join(
#         f"{name.upper() if name == 'id' else name}:{type_}"
#         for name, type_ in columns.items()
#     )

#     print(f"Таблица: {table_name}")
#     print(f"Столбцы: {structure}")
#     print(f"Количество записей: {len(data)}")

def run():
    """Запускает основной цикл работы базы данных."""
    print_help()
    available_commands = ["help","exit", "create_table", 
                        "list_tables", "drop_table", "insert", 
                        "select", "update", "delete", "info"]
    while True:
        user_command = prompt.string(prompt="Введите команду: ")

        if not user_command.strip():
            continue

        args = shlex.split(user_command)
        command = args[0].lower()

        if command not in available_commands:
            print(f'Функции {command} нет. Попробуйте снова.')
            continue
        
        if command == "help":
            print_help()
            continue

        elif command == "exit":
            break

        metadata = load_metadata(METADATA)

        try:
            if command == "create_table":
                table_name = args[1]
                columns = args[2:]
                result = create_table(metadata, table_name, columns)
                if result is not None:
                    save_metadata(METADATA, result)

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "drop_table":
                table_name = args[1]
                result = drop_table(metadata, table_name)
                if result is not None:
                    save_metadata(METADATA, result)

            elif command == "insert":
                table_name, values = parse_insert(args)
                insert(metadata, table_name, values)

            elif command == "select":
                table_name, where_clause = parse_select(args)
                table_data = load_table_data(table_name)
                result = select(table_data, where_clause)

                for row in result:
                    print(row)

            elif command == "update":
                table_name, set_clause, where_clause = parse_update(args)
                table_data = load_table_data(table_name)
                result = update(table_data, set_clause, where_clause)
                if result is not None:
                    save_table_data(table_name, result)
                    print(f'Записи в таблице "{table_name}" обновлены.')

            elif command == "delete":
                table_name, where_clause = parse_delete(args)
                table_data = load_table_data(table_name)
                result = delete(table_data, where_clause)
                if result is not None:
                    save_table_data(table_name, result)
                    print(f'Записи из таблицы "{table_name}" удалены.')

            elif command == "info":
                table_name = args[1]
                table_data = load_table_data(table_name)
                info(metadata, table_name, table_data)
        except (ValueError, IndexError) as error:
            print(f"Ошибка команды: {error}")

