import os
import struct
import heapq
from collections import defaultdict, Counter


class HuffmanCoder:
    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}

    class HuffmanNode:
        def __init__(self, char=None, freq=0, left=None, right=None):
            self.char = char
            self.freq = freq
            self.left = left
            self.right = right

        def __lt__(self, other):
            return self.freq < other.freq

    def build_huffman_tree(self, freq_dict):
        priority_queue = []
        for char, freq in freq_dict.items():
            heapq.heappush(priority_queue, self.HuffmanNode(char=char, freq=freq))

        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)
            merged = self.HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(priority_queue, merged)

        return heapq.heappop(priority_queue) if priority_queue else None

    def build_codes(self, node, current_code=""):
        if node is None:
            return

        if node.char is not None:
            self.codes[node.char] = current_code
            self.reverse_codes[current_code] = node.char
            return

        self.build_codes(node.left, current_code + "0")
        self.build_codes(node.right, current_code + "1")

    def encode_data(self, data):
        encoded_bits = ""
        for item in data:
            encoded_bits += self.codes[item]
        return encoded_bits

    def decode_data(self, encoded_bits):
        current_code = ""
        decoded_data = []
        for bit in encoded_bits:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded_data.append(self.reverse_codes[current_code])
                current_code = ""
        return decoded_data

    def serialize_tree(self, node, tree_bytes):
        if node.char is not None:
            tree_bytes.append(1)
            if isinstance(node.char, tuple):
                # Сериализация кортежа (тип, значение)
                tree_bytes.append(ord(node.char[0]))  # 'D', 'L' или 'C'
                if node.char[0] == 'C':  # Символ
                    tree_bytes.extend(node.char[1])
                else:  # Числовые значения (distance, length)
                    tree_bytes.extend(struct.pack('>H', node.char[1]))
            else:
                tree_bytes.extend(node.char)
        else:
            tree_bytes.append(0)
            self.serialize_tree(node.left, tree_bytes)
            self.serialize_tree(node.right, tree_bytes)

    @staticmethod
    def deserialize_tree(tree_data, index=0):
        if index >= len(tree_data):
            return None, index

        if tree_data[index] == 1:
            index += 1
            char_type = chr(tree_data[index])
            index += 1
            if char_type == 'C':
                char = tree_data[index:index + 1]
                index += 1
            else:
                char = (char_type, struct.unpack('>H', tree_data[index:index + 2])[0])
                index += 2
            return HuffmanCoder.HuffmanNode(char=char), index
        else:
            index += 1
            left, index = HuffmanCoder.deserialize_tree(tree_data, index)
            right, index = HuffmanCoder.deserialize_tree(tree_data, index)
            return HuffmanCoder.HuffmanNode(left=left, right=right), index


class LZ77HuffmanCompressor:
    def __init__(self, window_size=4096, lookahead_size=18):
        self.window_size = window_size
        self.lookahead_size = lookahead_size

    def compress(self, data):
        """LZ77 compression stage"""
        compressed = []
        i = 0
        len_data = len(data)

        while i < len_data:
            match_length = 0
            match_distance = 0
            next_char = data[i] if i < len_data else b''

            window_start = max(0, i - self.window_size)
            window = data[window_start:i]
            lookahead = data[i:i + self.lookahead_size]

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

            if match_length > 0:
                compressed.append((match_distance, match_length, next_char))
                i += match_length + (1 if next_char else 0)
            else:
                compressed.append((0, 0, data[i:i + 1]))
                i += 1

        return compressed

    def huffman_compress(self, lz77_data):
        """Huffman compression stage"""
        # Подготовка данных для Хаффмана
        freq_data = []
        for distance, length, char in lz77_data:
            freq_data.append(('D', distance))  # Маркер расстояния
            freq_data.append(('L', length))  # Маркер длины
            if char:
                freq_data.append(('C', char))  # Маркер символа

        # Подсчет частот
        freq_dict = Counter(freq_data)

        # Построение дерева Хаффмана
        huffman = HuffmanCoder()
        tree = huffman.build_huffman_tree(freq_dict)
        huffman.build_codes(tree)

        # Кодирование данных
        encoded_bits = huffman.encode_data(freq_data)

        # Сериализация дерева и данных
        tree_bytes = bytearray()
        huffman.serialize_tree(tree, tree_bytes)

        # Упаковка битов в байты
        encoded_bytes = bytearray()
        for i in range(0, len(encoded_bits), 8):
            byte = encoded_bits[i:i + 8]
            if len(byte) < 8:
                byte += '0' * (8 - len(byte))  # Дополнение
            encoded_bytes.append(int(byte, 2))

        return tree_bytes, encoded_bytes, len(encoded_bits)

    def serialize_compressed_data(self, tree_bytes, encoded_bytes, bit_length):
        """Сериализация сжатых данных"""
        header = struct.pack('>HHQ', self.window_size, self.lookahead_size, bit_length)
        return header + tree_bytes + encoded_bytes

    def calculate_compression_ratio(self, original_size, compressed_size):
        return original_size / compressed_size if compressed_size > 0 else 0


def read_file(filename):
    with open(filename, 'rb') as file:
        return file.read(1024*1024)


def write_compressed_file(filename, data):
    with open(filename, 'wb') as file:
        file.write(data)


def compress_file(input_filename, output_filename):
    try:
        # Чтение файла
        original_data = read_file(input_filename)
        original_size = len(original_data)

        # Сжатие
        compressor = LZ77HuffmanCompressor()
        lz77_data = compressor.compress(original_data)
        tree_bytes, encoded_bytes, bit_length = compressor.huffman_compress(lz77_data)
        compressed_data = compressor.serialize_compressed_data(tree_bytes, encoded_bytes, bit_length)
        compressed_size = len(compressed_data)

        # Запись сжатого файла
        write_compressed_file(output_filename, compressed_data)

        # Расчет коэффициента сжатия
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
    print("LZ77 + Huffman File Compressor")
    print("------------------------------")

    input_file = "C:\py projects\pythonProject1\enwik7.txt"
    output_file = "C:\py projects\pythonProject1\compressed.txt"

    if not output_file:
        output_file = "compressed.lz77ha"

    compress_file(input_file, output_file)