import unittest
from config_language import process_constants, evaluate_expression, convert_value, convert_dict

class TestConfigLanguage(unittest.TestCase):
    def test_process_constants(self):
        """Проверка обработки констант"""
        toml_data = {
            "def": {
                "pi": 3.14,
                "radius": 5
            }
        }
        constants = {}
        process_constants(toml_data, constants)
        self.assertIn("pi", constants)
        self.assertIn("radius", constants)
        self.assertEqual(constants["pi"], 3.14)
        self.assertEqual(constants["radius"], 5)

    def test_evaluate_expression(self):
        """Проверка вычисления выражений"""
        constants = {"pi": 3.14, "radius": 5}
        self.assertEqual(evaluate_expression("@(2 3 pow())", constants), 8)  # 2^3
        self.assertAlmostEqual(evaluate_expression("@(pi radius radius * *)", constants), 78.5)
        self.assertEqual(evaluate_expression("@(radius 2 pow())", constants), 25)

    def test_convert_value_simple(self):
        """Проверка преобразования простых значений"""
        constants = {}
        self.assertEqual(convert_value(42, constants), "42")
        self.assertEqual(convert_value(3.14, constants), "3.14")
        self.assertEqual(convert_value(True, constants), "True")
        self.assertEqual(convert_value("hello", constants), "hello")

    def test_convert_value_expression(self):
        """Проверка вычислений в значениях"""
        constants = {"pi": 3.14, "radius": 5}
        self.assertEqual(convert_value("@(pi radius radius * *)", constants), "78.5")

    def test_convert_dict_simple(self):
        """Проверка преобразования словаря"""
        constants = {}
        data = {
            "server": {
                "host": "127.0.0.1",
                "port": 8080,
                "debug": True
            }
        }
        expected_output = (
            "begin\n"
            "  server := begin\n"
            "    host := 127.0.0.1;\n"
            "    port := 8080;\n"
            "    debug := True;\n"
            "  end;\n"
            "end;"
        )
        result = convert_dict(data, constants)
        print(f"Результат:\n{result}")
        print(f"Ожидаемый результат:\n{expected_output}")
        self.assertEqual(result, expected_output)

    def test_convert_dict_nested(self):
        """Проверка вложенных словарей"""
        constants = {}
        data = {
            "playlist": {
                "name": "My Playlist",
                "tracks": ["Track1", "Track2", "Track3"],
                "metadata": {
                    "creator": "User123",
                    "likes": 150
                }
            }
        }
        expected_output = (
            "begin\n"
            "  playlist := begin\n"
            "    name := My Playlist;\n"
            "    tracks := [Track1, Track2, Track3];\n"
            "    metadata := begin\n"
            "      creator := User123;\n"
            "      likes := 150;\n"
            "    end;\n"
            "  end;\n"
            "end;"
        )
        result = convert_dict(data, constants)
        print(f"Результат:\n{result}")
        print(f"Ожидаемый результат:\n{expected_output}")
        self.assertEqual(result, expected_output)

    def test_invalid_key(self):
        """Проверка обработки некорректного имени ключа"""
        constants = {}
        data = {
            "invalid-key!": "value"
        }
        with self.assertRaises(ValueError) as context:
            convert_dict(data, constants)
        self.assertIn("Некорректное имя", str(context.exception))

    def test_empty_dict(self):
        """Проверка пустого словаря"""
        constants = {}
        data = {}
        expected_output = (
            "begin\n"
            "end;"
        )
        result = convert_dict(data, constants)
        print(f"Результат:\n{result}")
        print(f"Ожидаемый результат:\n{expected_output}")
        self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main()


