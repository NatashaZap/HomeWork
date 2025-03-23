import os


class BWT_RLE_Compressor:
    def __init__(self, block_size=1024):
        self.block_size = block_size

    def bwt_transform(self, data: bytes) -> (bytes, int):
        """Преобразование Барроуза-Уиллера"""
        if not data:
            return b'', 0

        data += b'\x00'
        n = len(data)
        rotations = [data[i:] + data[:i] for i in range(n)]
        rotations.sort()

        bwt_result = bytes(rot[-1] for rot in rotations)
        original_index = rotations.index(data)

        return bwt_result, original_index

    def rle_encode(self, data: bytes) -> bytes:
        """Кодирование длин серий (RLE)"""
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

    def compress_file(self, input_path: str, output_path: str):
        """Сжатие файла"""
        original_size = os.path.getsize(input_path)

        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            while True:
                block = fin.read(self.block_size)
                if not block:
                    break

                # Применяем BWT
                bwt_data, index = self.bwt_transform(block)

                # Применяем RLE
                rle_data = self.rle_encode(bwt_data)

                # Запись метаданных и данных
                fout.write(index.to_bytes(4, 'big'))
                fout.write(len(rle_data).to_bytes(4, 'big'))
                fout.write(rle_data)

        compressed_size = os.path.getsize(output_path)
        return original_size, compressed_size

    def decompress_file(self, input_path: str, output_path: str):
        """Распаковка файла"""
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            while True:
                index_bytes = fin.read(4)
                if not index_bytes:
                    break

                index = int.from_bytes(index_bytes, 'big')
                data_len = int.from_bytes(fin.read(4), 'big')
                rle_data = fin.read(data_len)

                # Декодирование RLE
                bwt_data = self.rle_decode(rle_data)

                # Обратное BWT преобразование
                original_data = self.inverse_bwt(bwt_data, index)
                fout.write(original_data)

    def rle_decode(self, data: bytes) -> bytes:
        """Декодирование RLE"""
        decoded = bytearray()
        i = 0
        n = len(data)

        while i < n:
            if i + 1 < n and data[i] == data[i + 1]:
                # Обработка повторяющихся символов
                count = data[i + 1]
                decoded.extend([data[i]] * count)
                i += 2
            else:
                decoded.append(data[i])
                i += 1

        return bytes(decoded)

    def inverse_bwt(self, bwt_data: bytes, index: int) -> bytes:
        """Обратное преобразование BWT"""
        if not bwt_data:
            return b''

        table = [bytearray() for _ in range(len(bwt_data))]
        for _ in range(len(bwt_data)):
            for i, c in enumerate(bwt_data):
                table[i].insert(0, c)
            table.sort()

        original = table[index]
        return bytes(original[:-1])  # Удаляем маркер конца


# Пример использования
if __name__ == "__main__":
    compressor = BWT_RLE_Compressor(block_size=1024)

    input_file = "D:\Pycharm projects\Help Natasha\enwik7.txt"
    compressed_file = "D:\Pycharm projects\Help Natasha\Compressed_files\compressed_bwt_rle.txt"
    original, compressed = compressor.compress_file(input_file, compressed_file)

    print(f"Original size: {original} bytes")
    print(f"Compressed size: {compressed} bytes")
    print(f"Compression ratio: {original / compressed:.2f}x")