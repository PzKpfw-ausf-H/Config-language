#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import toml

# Глобальный словарь для хранения констант
constants = {}

# Функция для обработки объявлений констант
def process_constants(toml_data):
    if 'def' in toml_data:
        for key, value in toml_data['def'].items():
            constants[key] = value
        del toml_data['def']

# Функция для вычисления константных выражений
def evaluate_expression(expr):
    tokens = expr.strip('@()').split()
    stack = []
    for token in tokens:
        if token in constants:
            stack.append(constants[token])
        elif token.isdigit():
            stack.append(int(token))
        elif is_number(token):
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
        elif token == 'abs()':
            if len(stack) < 1:
                raise ValueError("Недостаточно операндов для функции abs()")
            a = stack.pop()
            stack.append(abs(a))
        elif token == 'pow()':
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для функции pow()")
            b = stack.pop()
            a = stack.pop()
            stack.append(pow(a, b))
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
def convert_value(value):
    if isinstance(value, dict):
        return convert_dict(value)
    elif isinstance(value, list):
        converted_items = []
        for item in value:
            converted_items.append(convert_value(item))
        return '[' + ', '.join(converted_items) + ']'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if value.startswith('@(') and value.endswith(')'):
            result = evaluate_expression(value)
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
def convert_dict(d):
    output = "begin\n"
    for key, value in d.items():
        if not is_valid_name(key):
            raise ValueError(f"Некорректное имя: {key}")
        converted_value = convert_value(value)
        output += f" {key} := {converted_value};\n"
    output += "end"
    return output

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
        process_constants(toml_data)
        output_text = convert_dict(toml_data)
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
