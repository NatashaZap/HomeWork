import os
import struct
from collections import defaultdict


class LZ78Compressor:
    def __init__(self):
        self.dictionary = defaultdict(int)
        self.next_code = 1  # Начинаем с 1, так как 0 означает пустую строку

    def compress(self, data):
        """Сжимает данные с помощью алгоритма LZ78"""
        compressed = []
        current_phrase = ""

        for char in data:
            current_phrase += char
            if current_phrase not in self.dictionary:
                # Добавляем новую фразу в словарь
                self.dictionary[current_phrase] = self.next_code
                # Находим код префикса (все кроме последнего символа)
                prefix_code = self.dictionary.get(current_phrase[:-1], 0)
                # Сохраняем (код префикса, новый символ)
                compressed.append((prefix_code, char))
                self.next_code += 1
                current_phrase = ""

        # Обработка оставшейся фразы (если есть)
        if current_phrase:
            prefix_code = self.dictionary.get(current_phrase[:-1], 0)
            compressed.append((prefix_code, current_phrase[-1]))

        return compressed

    def decompress(self, compressed_data):
        dictionary = {0: ""}
        decompressed = []
        next_code = 1

        for code, char in compressed_data:
            # Получаем фразу из словаря
            phrase = dictionary[code] + char
            decompressed.append(phrase)
            # Добавляем новую фразу в словарь
            dictionary[next_code] = phrase
            next_code += 1

        return "".join(decompressed)

    def serialize_compressed_data(self, compressed_data):
        """Сериализует сжатые данные в бинарный формат"""
        binary_data = bytearray()

        for code, char in compressed_data:
            # Упаковываем код (4 байта) и символ (1 байт)
            binary_data.extend(struct.pack('>I', code))
            binary_data.extend(char.encode('utf-8') if isinstance(char, str) else char)

        return bytes(binary_data)

    def deserialize_compressed_data(self, binary_data):
        """Десериализует сжатые данные из бинарного формата"""
        compressed_data = []
        index = 0

        while index < len(binary_data):
            # Читаем код (4 байта)
            code = struct.unpack('>I', binary_data[index:index + 4])[0]
            index += 4
            # Читаем символ (1 байт)
            char = binary_data[index:index + 1].decode('utf-8')
            index += 1
            compressed_data.append((code, char))

        return compressed_data

    def calculate_compression_ratio(self, original_size, compressed_size):
        """Рассчитывает коэффициент сжатия"""
        return original_size / compressed_size if compressed_size > 0 else 0


def read_file(filename, mode='r'):
    """Читает содержимое файла"""
    with open(filename, mode) as file:
        return file.read(1024*1024)


def write_file(filename, data, mode='w'):
    """Записывает данные в файл"""
    with open(filename, mode) as file:
        file.write(data)


def compress_file(input_filename, output_filename):
    try:
        # Читаем исходный файл
        original_data = read_file(input_filename, 'rb')
        original_size = len(original_data)

        # Создаем компрессор
        compressor = LZ78Compressor()

        # Сжимаем данные
        compressed_data = compressor.compress(original_data.decode('utf-8'))

        # Сериализуем сжатые данные
        compressed_binary = compressor.serialize_compressed_data(compressed_data)
        compressed_size = len(compressed_binary)

        # Сохраняем сжатый файл
        write_file(output_filename, compressed_binary, 'wb')

        # Рассчитываем коэффициент сжатия
        compression_ratio = compressor.calculate_compression_ratio(original_size, compressed_size)

        print(f"Размер исходного файла: {original_size} байт")
        print(f"Размер сжатого файла: {compressed_size} байт")
        print(f"Коэффициент сжатия: {compression_ratio:.2f}")

        return True
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_filename}' не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    return False


def decompress_file(input_filename, output_filename):
    """Распаковывает файл, сжатый с помощью LZ78"""
    try:
        # Читаем сжатый файл
        compressed_binary = read_file(input_filename, 'rb')

        # Создаем компрессор
        compressor = LZ78Compressor()

        # Десериализуем данные
        compressed_data = compressor.deserialize_compressed_data(compressed_binary)

        # Распаковываем данные
        decompressed_data = compressor.decompress(compressed_data)

        # Сохраняем распакованный файл
        write_file(output_filename, decompressed_data, 'w')

        print(f"Файл '{input_filename}' успешно распакован в '{output_filename}'")
        return True
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_filename}' не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    return False


if __name__ == "__main__":
    print("LZ78 File Compressor/Decompressor")
    print("---------------------------------")

    input_file = "C:\py projects\pythonProject1\enwik7.txt"
    output_file = "C:\py projects\pythonProject1\compressed.txt"

    compress_file(input_file, output_file)