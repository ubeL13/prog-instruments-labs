import csv
import re
from typing import List, Optional
from checksum import calculate_checksum, serialize_result
import config


def csv_to_list(file_path: str) -> Optional[List[List[str]]]:
    """
    Читает данные из CSV файла.
    Args:
        file_path : Путь к файлу CSV.
    Returns:
        List : Список строк, каждая из которых представлена как список значений.
    """
    with open(file_path, "r", encoding="utf-16") as file:
        return [row for row in csv.reader(file, delimiter=";")][1:]


def is_valid(pattern: dict, row: List[str]) -> bool:
    """
    Проверяет, удовлетворяет ли строка регулярным выражениям.
    Args:
        row : Строка, представленная в виде списка значений.
        patterns : Словарь регулярных выражений.
    Returns:
        bool: True, если строка валидна, иначе False.
    """
    return all(re.match(pattern[key], data) for key, data in zip(pattern.keys(), row))


def find_invalid_indices(pattern: dict, data: List[List[str]]) -> Optional[List[int]]:
    """
    Находит индексы строк, которые не соответствуют требованиям.
    Args:
        data : Список строк для проверки.
        patterns : Словарь регулярных выражений.
    Returns:
        List : Список индексов невалидных строк.
    """
    return [i for i, row in enumerate(data) if not is_valid(pattern, row)]


def main():
    var_name = config.var
    input_csv = config.csv_file
    output_json = config.json_file
    regex_patterns = config.regulars

    csv_data = csv_to_list(input_csv)

    invalid_indices = find_invalid_indices(regex_patterns, csv_data)

    checksum_result = calculate_checksum(invalid_indices)
    serialize_result(var_name, checksum_result, output_json)


if __name__ == "__main__":
    main()
