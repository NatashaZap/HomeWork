import os
from heapq import heappush, heappop
from collections import defaultdict


class HuffmanCompressor:
    def __init__(self, block_size=4096):
        self.block_size = block_size

    class HuffmanNode:
        def __init__(self, char=None, freq=0):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq

    def _build_tree(self, freq_table):
        heap = []
        for char, freq in freq_table.items():
            heappush(heap, self.HuffmanNode(char, freq))

        while len(heap) > 1:
            left = heappop(heap)
            right = heappop(heap)
            merged = self.HuffmanNode(freq=left.freq + right.freq)
            merged.left = left
            merged.right = right
            heappush(heap, merged)

        return heappop(heap) if heap else None

    def _build_codes(self, root):
        codes = {}

        def traverse(node, code):
            if node:
                if node.char is not None:
                    codes[node.char] = code
                    return
                traverse(node.left, code + '0')
                traverse(node.right, code + '1')

        traverse(root, '')
        return codes

    def _encode_block(self, block):
        freq_table = defaultdict(int)
        for byte in block:
            freq_table[byte] += 1

        if not freq_table:
            return b'', {}, 0

        root = self._build_tree(freq_table)
        codes = self._build_codes(root)

        encoded_bits = ''.join(codes[byte] for byte in block)
        padding = 8 - (len(encoded_bits)) % 8
        encoded_bits += '0' * padding

        encoded_bytes = bytes(int(encoded_bits[i:i+8], 2) for i in range(0, len(encoded_bits), 8))

        return encoded_bytes, freq_table, padding

    def compress_file(self, input_path):
        original_size = os.path.getsize(input_path)
        total_compressed = 0
        metadata_size = 0

        with open(input_path, 'rb') as fin:
            while True:
                block = fin.read(self.block_size)
                if not block:
                    break

                # Кодирование блока
                encoded, freq_table, padding = self._encode_block(block)

                # Запись метаданных
                metadata = self._pack_metadata(freq_table, padding)

                # Расчет размеров
                total_compressed += len(metadata) + len(encoded)
                metadata_size += len(metadata)

        # Расчет метрик
        compression_ratio = original_size / total_compressed if total_compressed > 0 else 0
        efficiency = (1 - (total_compressed / original_size)) * 100 if original_size > 0 else 0

        print(f"{'Original Size:':<20} {original_size} bytes")
        print(f"{'Compressed Size:':<20} {total_compressed} bytes")
        print(f"{'Metadata Size:':<20} {metadata_size} bytes")
        print(f"{'Compression Ratio:':<20} {compression_ratio:.2f}x")
        print(f"{'Space Saving:':<20} {efficiency:.1f}%")

    def _pack_metadata(self, freq_table, padding):
        metadata = bytearray()
        # Формат: [padding (1 byte)] [freq_table (256 * 4 bytes)]
        metadata.append(padding)
        for i in range(256):
            freq = freq_table.get(i, 0)
            metadata += freq.to_bytes(4, 'big')
        return bytes(metadata)


# Пример использования
if __name__ == "__main__":
    compressor = HuffmanCompressor(block_size=4096)

    compressor.compress_file("D:\Pycharm projects\Help Natasha\enwik7.txt")