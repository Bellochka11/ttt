import time
from functools import wraps


def handle_db_errors(func):
    """Обрабатывает ошибки при работе с базой данных."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as error:
            print(f"Таблица не найдена: {error}")
        except ValueError as error:
            print(f"Ошибка валидации данных: {error}")
        except FileNotFoundError as error:
            print(f"Файл не найден: {error}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед выполнением действия."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """Измеряет и выводит время выполнения функции."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(
                f"Функция {func.__name__} выполнилась "
                f"за {elapsed:.3f} секунд"
            )
    return wrapper


def create_cacher():
    """Создаёт кеш для сохранения результатов вызовов."""
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
    return cache_result

