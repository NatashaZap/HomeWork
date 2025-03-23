import matplotlib.pyplot as plt


def compress_lzss(data, window_size, max_match_length=15):
    """Упрощенная реализация LZSS с заданным размером буфера поиска."""
    compressed = []
    current_pos = 0
    data_len = len(data)

    while current_pos < data_len:
        best_match = (0, 0)  # (смещение, длина)

        # Границы буфера поиска
        search_start = max(0, current_pos - window_size)
        search_end = current_pos

        # Поиск наилучшего совпадения
        for i in range(search_start, search_end):
            match_length = 0
            # Проверяем совпадение символов
            while (current_pos + match_length < data_len and
                   i + match_length < search_end and
                   data[i + match_length] == data[current_pos + match_length]):
                match_length += 1
                if match_length >= max_match_length:
                    break  # Ограничение длины совпадения
            if match_length > best_match[1]:
                best_match = (current_pos - i, match_length)  # Смещение = текущая позиция - позиция совпадения

        # Если найдено совпадение длиной >= 2 символов
        if best_match[1] >= 2:
            compressed.append((best_match[0], best_match[1]))
            current_pos += best_match[1]
        else:
            compressed.append(data[current_pos])
            current_pos += 1

    return compressed


def calculate_compression_ratio(original_data, compressed_data):
    """Расчет коэффициента сжатия (original_size / compressed_size)."""
    # Оригинальный размер в байтах
    original_size = len(original_data)

    # Расчет размера сжатых данных
    compressed_size = 0
    for element in compressed_data:
        if isinstance(element, tuple):
            # Кодирование совпадения: 2 байта (смещение) + 1 байт (длина)
            compressed_size += 3
        else:
            # Кодирование литерала: 1 байт
            compressed_size += 1

    return original_size / compressed_size if compressed_size != 0 else 0


if __name__ == "__main__":
    with open(r'D:\Pycharm projects\Help Natasha\enwik7.txt', 'rb') as f:
        test_data = f.read(1024 * 1024)

    # Параметры для тестирования
    window_sizes = [64, 128, 256, 512, 1024, 2048]
    compression_ratios = []

    # Тестирование для разных размеров буфера
    print(f"Исходный размер данных: {len(test_data)} байт")
    print("{:<10} | {:<10} | {:<10} | {:<10}".format(
        "Буфер", "Сжатый", "Коэффициент", "Эффективность"
    ))
    print("-" * 50)

    for window_size in window_sizes:
        compressed = compress_lzss(test_data, window_size)
        ratio = calculate_compression_ratio(test_data, compressed)
        compressed_size = len(test_data) / ratio if ratio != 0 else 0
        efficiency = (1 - 1 / ratio) * 100 if ratio != 0 else 0

        print("{:<10} | {:<10.1f} | {:<10.2f} | {:<10.1f}%".format(
            window_size,
            compressed_size,
            ratio,
            efficiency
        ))
        compression_ratios.append(ratio)

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(window_sizes, compression_ratios, marker='o', linestyle='-', color='b')
    plt.xlabel('Размер буфера поиска (байты)')
    plt.ylabel('Коэффициент сжатия')
    plt.title('Зависимость коэффициента сжатия от размера буфера (LZSS)')
    plt.grid(True)
    plt.show()