import heapq
from collections import Counter
import json


class LZ78Compressor:
    def compress(self, data):
        """Сжимает данные с помощью алгоритма LZ78."""
        dictionary = {}
        result = []
        current_index = 1
        i = 0

        while i < len(data):
            current_phrase = ""
            while i < len(data) and (current_phrase + data[i]) in dictionary:
                current_phrase += data[i]
                i += 1

            if i < len(data):
                current_phrase += data[i]
                i += 1

            prefix = current_phrase[:-1]
            last_char = current_phrase[-1] if len(current_phrase) > 0 else ''
            prefix_index = dictionary.get(prefix, 0)
            result.append((prefix_index, last_char))

            if current_phrase not in dictionary:
                dictionary[current_phrase] = current_index
                current_index += 1

        return result

    def decompress(self, compressed_data):
        """Восстанавливает данные из сжатого формата LZ78."""
        dictionary = {0: ''}
        result = []
        current_index = 1

        for index, char in compressed_data:
            phrase = dictionary[index] + char
            result.append(phrase)
            dictionary[current_index] = phrase
            current_index += 1

        return ''.join(result)

    def compress_to_bytes(self, data):
        """Конвертирует сжатые данные в байтовый поток."""
        byte_stream = bytearray()
        for index, char in self.compress(data):
            byte_stream.extend(index.to_bytes(4, 'big'))
            byte_stream.extend(ord(char).to_bytes(4, 'big'))
        return bytes(byte_stream)

    def decompress_from_bytes(self, byte_data):
        """Восстанавливает данные из байтового потока."""
        compressed = []
        for i in range(0, len(byte_data), 8):
            index = int.from_bytes(byte_data[i:i + 4], 'big')
            char = chr(int.from_bytes(byte_data[i + 4:i + 8], 'big'))
            compressed.append((index, char))
        return self.decompress(compressed)

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCompressor:
    def build_huffman_tree(self, data):
        frequency = Counter(data)
        heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, merged)

        return heap[0]

    def build_codes(self, node, current_code="", codes={}):
        if node is None:
            return

        if node.char is not None:
            codes[node.char] = current_code
            return

        self.build_codes(node.left, current_code + "0", codes)
        self.build_codes(node.right, current_code + "1", codes)
        return codes

    def compress(self, data):
        """Сжимает данные с помощью алгоритма Хаффмана."""
        root = self.build_huffman_tree(data)
        codes = self.build_codes(root)
        encoded = ''.join([codes[char] for char in data])
        return encoded, codes

    def decompress(self, encoded_data, codes):
        """Распаковывает данные, сжатые алгоритмом Хаффмана."""
        reverse_mapping = {v: k for k, v in codes.items()}
        current_code = ""
        result = []

        for bit in encoded_data:
            current_code += bit
            if current_code in reverse_mapping:
                result.append(reverse_mapping[current_code])
                current_code = ""

        return ''.join(result)


class LZ78HuffmanCompressor:
    def __init__(self):
        self.lz78 = LZ78Compressor()
        self.huffman = HuffmanCompressor()
        self.original_size = 0  # Размер исходных данных в байтах
        self.compressed_size = 0  # Размер сжатых данных в байтах

    def compress_file(self, input_path, output_path):
        # Чтение и расчет исходного размера
        with open(input_path, 'r', encoding='utf-8') as f:
            original_data = f.read()
            self.original_size = len(original_data.encode('utf-8'))

            # Сжатие LZ78
            lz78_bytes = self.lz78.compress_to_bytes(original_data)
            lz78_str = lz78_bytes.decode('latin-1')

            # Сжатие Хаффманом
            huffman_encoded, huffman_codes = self.huffman.compress(lz78_str)

            # Формирование метаданных
            padding = 8 - (len(huffman_encoded) % 8)
            huffman_encoded += '0' * padding

            # Сериализация кодов Хаффмана
            serializable_codes = {ord(k): v for k, v in huffman_codes.items()}
            metadata = {
                'padding': padding,
                'codes': serializable_codes
            }

            # Запись в файл
            with open(output_path, 'wb') as f:
                # Запись метаданных
                metadata_json = json.dumps(metadata).encode('utf-8')
                f.write(len(metadata_json).to_bytes(4, 'big'))
                f.write(metadata_json)

                # Запись сжатых данных
                byte_array = bytearray()
                for i in range(0, len(huffman_encoded), 8):
                    byte = int(huffman_encoded[i:i + 8], 2)
                    byte_array.append(byte)
                f.write(bytes(byte_array))

        # Расчет общего размера сжатого файла
        metadata_json = json.dumps(metadata).encode('utf-8')
        self.compressed_size = (
                4 +  # Размер заголовка метаданных
                len(metadata_json) +
                len(byte_array))

        return self.get_compression_ratio()

    def get_compression_ratio(self):

        if self.compressed_size == 0:
            return 0.0
        return self.original_size / self.compressed_size

    def print_compression_info(self):
        """Выводит подробную статистику сжатия."""
        print(f"Original size: {self.original_size} bytes")
        print(f"Compressed size: {self.compressed_size} bytes")
        print(f"Compression ratio: {self.get_compression_ratio():.2f}:1")
        print(f"Space saving: {(1 - 1 / self.get_compression_ratio()) * 100:.1f}%")


if __name__ == '__main__':
    compressor = LZ78HuffmanCompressor()

    input_file = 'D:\Pycharm projects\Help Natasha\enwik7.txt'
    output_file = 'D:\Pycharm projects\Help Natasha\Compressed_files\compressed_file.bin'
    ratio = compressor.compress_file(input_file, output_file)
    print(f"Compression ratio: {ratio:.2f}:1")

    compressor.print_compression_info()