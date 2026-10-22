def convert_value(value):
    """Преобразует значение в соответствии с указанным типом данных."""
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value



def parse_insert(args):
    """Разбирает команду добавления записи."""
    table_name = args[2]
    values_string = " ".join(args[4:])
    values_string = values_string.strip("()")
    values = [
        convert_value(value)
        for value in values_string.split(",")
    ]
    return table_name, values


def parse_select(args):
    """Разбирает команду выборки записей."""
    table_name = args[2]
    where_clause = None
    if "where" in args:
        where_index = args.index("where")
        column = args[where_index + 1]
        value = args[where_index + 3]
        if value.isdigit():
            value = int(value)
        elif value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        where_clause = {column: value}
    return table_name, where_clause



def parse_update(args):
    """Разбирает команду обновления записей."""
    table_name = args[1]
    set_index = args.index("set")
    where_index = args.index("where")

    set_column = args[set_index + 1]
    set_value = args[set_index + 3]

    where_column = args[where_index + 1]
    where_value = args[where_index + 3]

    set_value = convert_value(set_value)
    where_value = convert_value(where_value)

    set_clause = {set_column: set_value}
    where_clause = {where_column: where_value}
    
    return table_name, set_clause, where_clause


def parse_delete(args):
    """Разбирает команду удаления записей."""
    table_name = args[2]
    where_index = args.index("where")
    column = args[where_index + 1]
    value = args[where_index + 3]
    value = convert_value(value)
    where_clause = {column: value}
    return table_name, where_clause