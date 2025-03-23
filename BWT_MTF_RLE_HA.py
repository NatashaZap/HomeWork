import os
from heapq import heappush, heappop, heapify
from collections import defaultdict, Counter


class BWT_MTF_RLE_HA_Compressor:
    def __init__(self, block_size=1024):
        self.block_size = block_size

    # BWT Implementation
    def bwt_transform(self, data: bytes) -> tuple[bytes, int]:
        if not data:
            return b'', 0
        data += b'\x00'
        n = len(data)
        rotations = sorted(data[i:] + data[:i] for i in range(n))
        bwt_result = bytes(rot[-1] for rot in rotations)
        return bwt_result, rotations.index(data)

    # MTF Implementation
    def mtf_encode(self, data: bytes) -> bytes:
        dictionary = list(range(256))
        encoded = []
        for byte in data:
            idx = dictionary.index(byte)
            encoded.append(idx)
            dictionary.pop(idx)
            dictionary.insert(0, byte)
        return bytes(encoded)

    # RLE Implementation
    def rle_encode(self, data: bytes) -> bytes:
        encoded = bytearray()
        i = 0
        n = len(data)
        while i < n:
            count = 1
            while i + 1 < n and data[i] == data[i + 1] and count < 255:
                count += 1
                i += 1
            if count > 1:
                encoded.extend([data[i], count])
            else:
                encoded.append(data[i])
            i += 1
        return bytes(encoded)

    # Huffman Implementation
    class HuffmanNode:
        def __init__(self, char=None, freq=0):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq

    def build_huffman_tree(self, freq_table):
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

    def huffman_encode(self, data: bytes) -> tuple[bytes, dict, int]:
        freq_table = Counter(data)
        root = self.build_huffman_tree(freq_table)
        codes = self.build_codes(root)

        encoded_bits = ''.join(codes[byte] for byte in data)
        padding = 8 - (len(encoded_bits) % 8)
        encoded_bits += '0' * padding

        encoded_bytes = bytes(
            int(encoded_bits[i:i + 8], 2)
            for i in range(0, len(encoded_bits), 8)
        )
        return encoded_bytes, freq_table, padding

    def build_codes(self, root):
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

    # Compression Pipeline
    def compress_file(self, input_path: str, output_path: str):
        original_size = os.path.getsize(input_path)

        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            while True:
                block = fin.read(self.block_size)
                if not block:
                    break

                # BWT
                bwt_data, index = self.bwt_transform(block)

                # MTF
                mtf_data = self.mtf_encode(bwt_data)

                # RLE
                rle_data = self.rle_encode(mtf_data)

                # Huffman
                encoded, freq_table, padding = self.huffman_encode(rle_data)

                # Write metadata
                fout.write(index.to_bytes(4, 'big'))
                fout.write(padding.to_bytes(1, 'big'))
                fout.write(len(freq_table).to_bytes(2, 'big'))
                for char, freq in freq_table.items():
                    fout.write(bytes([char]))
                    fout.write(freq.to_bytes(4, 'big'))

                # Write compressed data
                fout.write(len(encoded).to_bytes(4, 'big'))
                fout.write(encoded)

        compressed_size = os.path.getsize(output_path)
        return original_size, compressed_size

    # Decompression Pipeline
    def decompress_file(self, input_path: str, output_path: str):
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            while True:
                try:
                    # Read metadata
                    index = int.from_bytes(fin.read(4), 'big')
                    padding = int.from_bytes(fin.read(1), 'big')
                    freq_table_size = int.from_bytes(fin.read(2), 'big')

                    freq_table = {}
                    for _ in range(freq_table_size):
                        char = ord(fin.read(1))
                        freq = int.from_bytes(fin.read(4), 'big')
                        freq_table[char] = freq

                    data_len = int.from_bytes(fin.read(4), 'big')
                    encoded_data = fin.read(data_len)

                    # Huffman decode
                    rle_data = self.huffman_decode(encoded_data, freq_table, padding)

                    # RLE decode
                    mtf_data = self.rle_decode(rle_data)

                    # MTF decode
                    bwt_data = self.mtf_decode(mtf_data)

                    # Inverse BWT
                    original_block = self.inverse_bwt(bwt_data, index)
                    fout.write(original_block)
                except EOFError:
                    break

    def huffman_decode(self, data, freq_table, padding):
        root = self.build_huffman_tree(freq_table)
        bit_str = ''.join(f"{byte:08b}" for byte in data)
        bit_str = bit_str[:-padding] if padding > 0 else bit_str

        decoded = []
        node = root
        for bit in bit_str:
            node = node.left if bit == '0' else node.right
            if node.char is not None:
                decoded.append(node.char)
                node = root
        return bytes(decoded)

    def rle_decode(self, data: bytes) -> bytes:
        decoded = bytearray()
        i = 0
        n = len(data)
        while i < n:
            if i + 1 < n and data[i] == data[i + 1]:
                count = data[i + 1]
                decoded.extend([data[i]] * count)
                i += 2
            else:
                decoded.append(data[i])
                i += 1
        return bytes(decoded)

    def mtf_decode(self, data: bytes) -> bytes:
        dictionary = list(range(256))
        decoded = []
        for idx in data:
            char = dictionary[idx]
            decoded.append(char)
            dictionary.pop(idx)
            dictionary.insert(0, char)
        return bytes(decoded)

    def inverse_bwt(self, bwt_data: bytes, index: int) -> bytes:
        table = [bytearray() for _ in range(len(bwt_data))]
        for _ in range(len(bwt_data)):
            for i, c in enumerate(bwt_data):
                table[i].insert(0, c)
            table.sort()
        return bytes(table[index][:-1])


# Пример использования
if __name__ == "__main__":
    compressor = BWT_MTF_RLE_HA_Compressor(block_size=1024)

    # Сжатие
    input_file = "D:\Pycharm projects\Help Natasha\enwik7.txt"
    compressed_file = "D:\Pycharm projects\Help Natasha\Compressed_files\compressed_bwt_rle.txt"
    original, compressed = compressor.compress_file(input_file, compressed_file)

    print(f"Исходный размер: {original} байт")
    print(f"Сжатый размер: {compressed} байт")
    print(f"Коэффициент сжатия: {original / compressed:.2f}x")
