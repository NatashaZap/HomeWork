def rle_encode(data):
    """Функция для сжатия данных с помощью алгоритма RLE."""
    if not data:
        return ""

    encoded = []
    count = 1
    previous_char = data[0]

    for char in data[1:]:
        if char == previous_char:
            count += 1
        else:
            encoded.append(f"{previous_char}{count}")
            previous_char = char
            count = 1

    # Добавляем последний набор символов
    encoded.append(f"{previous_char}{count}")

    return ''.join(encoded)

def rle_decode(encoded):
    """Функция для декодирования данных, закодированных с помощью алгоритма RLE."""
    decoded = []
    i = 0

    while i < len(encoded):
        char = encoded[i]
        i += 1
        count = 0

        # Читаем количество повторений
        while i < len(encoded) and encoded[i].isdigit():
            count = count * 10 + int(encoded[i])  # Формируем число
            i += 1

        decoded.append(char * count)  # Восстанавливаем символы

    return ''.join(decoded)

def calculate_compression_ratio(original, encoded):
    """Функция для расчета коэффициента сжатия."""
    if not original:
        return 0  # Избегаем деления на ноль
    return len(original) / len(encoded)

# Пример использования
if __name__ == "__main__":

    input_file = 'D:\Pycharm projects\Help Natasha\enwik7.txt'
    output_file = 'D:\Pycharm projects\Help Natasha\Compressed_files\compressed_RLE.txt'

    with open(input_file, 'rb') as f, open(output_file, 'w') as fout:
        original_text = f.read(1024 * 1024)

        # Размер оригинального текста
        original_size = len(original_text)
        print(f"Размер оригинального текста: {original_size} байт")

        # Сжатие текста
        encoded_text = rle_encode(original_text)
        fout.write(encoded_text)

        # Размер закодированного текста
        encoded_size = len(encoded_text)
        print(f"Размер закодированного текста: {encoded_size} байт")

        # Расчет коэффициента сжатия
        compression_ratio = calculate_compression_ratio(original_text, encoded_text)
        print("Коэффициент сжатия:", compression_ratio)
