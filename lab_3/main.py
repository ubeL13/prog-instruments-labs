import csv
import re
import json
from typing import List
from checksum import calculate_checksum, serialize_result


def load_settings(file_path: str) -> dict:
    """Загружает настройки из JSON файла.

    Args:
        file_path : Путь к конфигурационному файлу.

    Returns:
        dict: Словарь с настройками.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def read_csv(file_path: str) -> List[List[str]]:
    """Читает данные из CSV файла.

    Args:
        file_path : Путь к файлу CSV.

    Returns:
        List : Список строк, каждая из которых представлена как список значений.
    """
    with open(file_path, "r", encoding="utf-16") as file:
        return [row for row in csv.reader(file, delimiter=";")][1:]


def is_valid(row: List[str], patterns: dict) -> bool:
    """Проверяет, удовлетворяет ли строка регулярным выражениям.

    Args:
        row : Строка, представленная в виде списка значений.
        patterns : Словарь регулярных выражений.

    Returns:
        bool: True, если строка валидна, иначе False.
    """
    return all(re.match(patterns[field], value) for field, value in zip(patterns.keys(), row))


def find_invalid_indices(data: List[List[str]], patterns: dict) -> List[int]:
    """Находит индексы строк, которые не соответствуют требованиям.

    Args:
        data : Список строк для проверки.
        patterns : Словарь регулярных выражений.

    Returns:
        List : Список индексов невалидных строк.
    """
    return [index for index, row in enumerate(data) if not is_valid(row, patterns)]


def main():
    settings = load_settings("config.json")

    var_name = settings["VAR"]
    input_csv = settings["CSV_FILE"]
    output_json = settings["JSON_FILE"]
    regex_patterns = settings["REGULARS"]

    csv_data = read_csv(input_csv)
    invalid_indices = find_invalid_indices(csv_data, regex_patterns)

    checksum_result = calculate_checksum(invalid_indices)
    serialize_result(var_name, checksum_result, output_json)


if __name__ == "__main__":
    main()
