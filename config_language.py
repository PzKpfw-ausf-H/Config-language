#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import toml
import re

# Глобальный словарь для хранения констант
constants = {}

# Функция для обработки объявлений констант
def process_constants(toml_data, constants):
    if 'def' in toml_data:
        for key, value in toml_data['def'].items():
            if not key.isidentifier():
                raise ValueError(f"Некорректное имя для константы: {key}")
            constants[key] = value
        del toml_data['def']

# Функция для вычисления константных выражений
def evaluate_expression(expr, constants):
    import re
    tokens = re.findall(r'\w+|\S', expr.strip('@()'))  # Корректное разделение токенов
    stack = []
    for token in tokens:
        print(f"Обработка токена: {token}")  # Отладочный вывод
        if token in constants:
            stack.append(constants[token])
        elif token.isdigit():
            stack.append(int(token))
        elif re.match(r'^\d+\.\d+$', token):  # Проверка числа с плавающей точкой
            stack.append(float(token))
        elif token in ['+', '-', '*']:
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для операции")
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
        elif token == 'pow':
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для функции pow")
            b = stack.pop()
            a = stack.pop()
            stack.append(pow(a, b))
        elif token == 'abs()':
            if len(stack) < 1:
                raise ValueError("Недостаточно операндов для функции abs()")
            a = stack.pop()
            stack.append(abs(a))
        else:
            raise ValueError(f"Неизвестный токен в выражении: {token}")
    if len(stack) != 1:
        raise ValueError("Неверное выражение")
    return stack[0]




def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Функция для преобразования значений
def convert_value(value, constants):
    if isinstance(value, dict):
        return convert_dict(value, constants)
    elif isinstance(value, list):
        converted_items = []
        for item in value:
            converted_items.append(convert_value(item, constants))
        return '[' + ', '.join(converted_items) + ']'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if value.startswith('@(') and value.endswith(')'):
            result = evaluate_expression(value, constants)
            return str(result)
        else:
            return value
    elif isinstance(value, bool):
        return str(value)
    else:
        raise ValueError(f"Неподдерживаемый тип значения: {type(value)}")

# Функция для проверки корректности имени
def is_valid_name(name):
    return name.isidentifier()

# Функция для преобразования словарей
def convert_dict(d, constants, indent_level=0):
    indent = " " * (indent_level * 2)
    output = f"{indent}begin\n"
    for key, value in d.items():
        if not key.isidentifier():
            raise ValueError(f"Некорректное имя: {key}")
        if isinstance(value, dict):
            converted_value = convert_dict(value, constants, indent_level + 1)
            output += f"{indent}  {key} := {converted_value.strip()}\n"
        else:
            converted_value = convert_value(value, constants)
            output += f"{indent}  {key} := {converted_value};\n"
    output += f"{indent}end;"
    return output.strip()  # Убираем лишние пробелы



def main():
    parser = argparse.ArgumentParser(description='Инструмент преобразования TOML в учебный конфигурационный язык.')
    parser.add_argument('-o', '--output', required=True, help='Путь к выходному файлу')
    args = parser.parse_args()

    try:
        toml_data = toml.load(sys.stdin)
    except toml.TomlDecodeError as e:
        sys.stderr.write(f"Ошибка парсинга TOML: {e}\n")
        sys.exit(1)

    try:
        process_constants(toml_data, constants)  # Передаём `constants`
        output_text = convert_dict(toml_data, constants)
    except ValueError as e:
        sys.stderr.write(f"Ошибка преобразования: {e}\n")
        sys.exit(1)

    try:
        with open(args.output, 'w') as f:
            f.write(output_text)
    except IOError as e:
        sys.stderr.write(f"Ошибка записи в файл: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
