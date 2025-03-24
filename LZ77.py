import os
import struct


class LZ77Compressor:
    def __init__(self, window_size=4096, lookahead_size=18):
        self.window_size = window_size
        self.lookahead_size = lookahead_size

    def compress(self, data):
        """Сжимает данные с помощью алгоритма LZ77."""
        compressed_data = []
        i = 0
        len_data = len(data)

        while i < len_data:
            match_length = 0
            match_distance = 0
            next_char = data[i] if i < len_data else b''

            # Устанавливаем границы окна и области поиска
            window_start = max(0, i - self.window_size)
            window = data[window_start:i]
            lookahead = data[i:i + self.lookahead_size]

            # Поиск наилучшего совпадения
            for j in range(len(window)):
                length = 0
                while (length < len(lookahead) and
                       j + length < len(window) and
                       window[j + length] == lookahead[length]):
                    length += 1

                if length > match_length:
                    match_length = length
                    match_distance = len(window) - j
                    if match_length < len(lookahead):
                        next_char = lookahead[match_length:match_length + 1]
                    else:
                        next_char = b''

            # Если совпадение найдено, добавляем его в сжатые данные
            if match_length > 0:
                compressed_data.append((match_distance, match_length, next_char))
                i += match_length + (1 if next_char else 0)
            else:
                compressed_data.append((0, 0, data[i:i + 1]))
                i += 1

        return compressed_data

    def serialize_compressed_data(self, compressed_data):
        """Сериализует сжатые данные в бинарный формат."""
        binary_data = bytearray()

        # Записываем заголовок (размер окна и lookahead)
        binary_data.extend(struct.pack('>HH', self.window_size, self.lookahead_size))

        for distance, length, char in compressed_data:
            # Упаковываем distance (2 байта), length (1 байт) и char (1 байт)
            binary_data.extend(struct.pack('>HB', distance, length))
            binary_data.extend(char if char else b'\x00')

        return bytes(binary_data)

    def calculate_compression_ratio(self, original_size, compressed_size):
        """Рассчитывает коэффициент сжатия."""
        return original_size / compressed_size if compressed_size > 0 else 0


def read_file(filename):
    """Читает содержимое файла в бинарном режиме."""
    with open(filename, 'rb') as file:
        return file.read(1024*100)


def write_compressed_file(filename, compressed_data):
    """Записывает сжатые данные в файл."""
    with open(filename, 'wb') as file:
        file.write(compressed_data)


def compress_file(input_filename, output_filename):
    try:
        original_data = read_file(input_filename)
        original_size = len(original_data)

        compressor = LZ77Compressor()

        compressed_tuples = compressor.compress(original_data)

        compressed_binary = compressor.serialize_compressed_data(compressed_tuples)
        compressed_size = len(compressed_binary)

        # Сохраняем сжатый файл
        write_compressed_file(output_filename, compressed_binary)

        compression_ratio = compressor.calculate_compression_ratio(original_size, compressed_size)

        print(f"Файл '{input_filename}' успешно сжат и сохранен как '{output_filename}'")
        print(f"Размер исходного файла: {original_size} байт")
        print(f"Размер сжатого файла: {compressed_size} байт")
        print(f"Коэффициент сжатия: {compression_ratio:.2f}")

        return True
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_filename}' не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    return False


if __name__ == "__main__":
    print("LZ77 File Compressor")
    print("--------------------")

    input_file = "C:\py projects\pythonProject1\enwik7.txt"
    output_file = "C:\py projects\pythonProject1\compressed.txt"

    compress_file(input_file, output_file)