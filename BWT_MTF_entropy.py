import math
import matplotlib.pyplot as plt


def calculate_entropy(data: bytes) -> float:
    """Вычисление энтропии Шеннона для байтовой строки"""
    if not data:
        return 0.0

    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1

    entropy = 0.0
    total = len(data)
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy


def bwt_transform(block: bytes) -> bytes:
    """BWT преобразование для блока данных"""
    if not block:
        return b''

    # Добавляем маркер конца данных
    block += b'\x00'
    rotations = [block[i:] + block[:i] for i in range(len(block))]
    rotations.sort()
    bwt_result = bytes([rot[-1] for rot in rotations])
    return bwt_result


def mtf_transform(data: bytes) -> bytes:
    """MTF преобразование"""
    dictionary = list(range(256))
    result = []

    for byte in data:
        idx = dictionary.index(byte)
        result.append(idx)
        # Перемещаем символ в начало
        del dictionary[idx]
        dictionary.insert(0, byte)

    return bytes(result)


def analyze_entropy(data: bytes, max_block_size: int = 4096) -> dict:
    """Анализ энтропии для разных размеров блоков"""
    results = {}

    for block_size in [64, 128, 256, 512, 1024, 2048, 4096]:
        if block_size > max_block_size:
            continue

        total_entropy = 0.0
        blocks = 0

        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]

            # Применяем BWT+MTF
            bwt_block = bwt_transform(block)
            mtf_block = mtf_transform(bwt_block)

            # Считаем энтропию
            entropy = calculate_entropy(mtf_block)
            total_entropy += entropy
            blocks += 1

        avg_entropy = total_entropy / blocks if blocks > 0 else 0
        results[block_size] = avg_entropy

    return results


def plot_results(results: dict):
    """Визуализация результатов"""
    sizes = sorted(results.keys())
    entropies = [results[size] for size in sizes]

    plt.figure(figsize=(10, 6))
    plt.plot(sizes, entropies, 'bo-')
    plt.xlabel('Размер блока (байт)')
    plt.ylabel('Энтропия (бит/байт)')
    plt.title('Зависимость энтропии от размера блока')
    plt.grid(True)
    plt.xticks(sizes)
    plt.show()


def analyze_compression(data: bytes, max_block_size: int = 4096) -> dict:
    """Анализ энтропии и коэффициента сжатия для разных размеров блоков"""
    results = {}

    for block_size in [64, 128, 256, 512, 1024, 2048, 4096]:
        if block_size > max_block_size:
            continue

        total_entropy = 0.0
        total_compressed = 0
        total_original = 0
        blocks = 0

        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            if not block:
                continue

            # Применяем цепочку преобразований
            bwt_block = bwt_transform(block)
            mtf_block = mtf_transform(bwt_block)

            # Считаем метрики
            entropy = calculate_entropy(mtf_block)
            total_entropy += entropy
            total_compressed += len(mtf_block)
            total_original += len(block)
            blocks += 1

        avg_entropy = total_entropy / blocks if blocks > 0 else 0
        compression_ratio = total_original / total_compressed if total_compressed > 0 else 0
        efficiency = (1 - (total_compressed / total_original)) * 100 if total_original > 0 else 0

        results[block_size] = {
            'block_size': block_size,
            'original_size': total_original,
            'compressed_size': total_compressed,
            'compression_ratio': compression_ratio,
            'efficiency': efficiency,
            'entropy': avg_entropy
        }

    return results


def print_results_table(results: dict):
    """Вывод результатов в виде таблицы"""
    print("\n{:<10} {:<12} {:<14} {:<18} {:<12} {:<10}".format(
        'Block Size', 'Original (B)', 'Compressed (B)',
        'Compression Ratio', 'Efficiency (%)', 'Entropy (b/B)'
    ))
    print("-" * 85)

    for size in sorted(results.keys()):
        res = results[size]
        print("{:<10} {:<12} {:<14} {:<18.2f} {:<12.1f} {:<10.3f}".format(
            res['block_size'],
            res['original_size'],
            res['compressed_size'],
            res['compression_ratio'],
            res['efficiency'],
            res['entropy']
        ))


def plot_combined_results(results: dict):
    """Визуализация энтропии и коэффициента сжатия"""
    sizes = sorted(results.keys())
    entropies = [results[size]['entropy'] for size in sizes]
    ratios = [results[size]['compression_ratio'] for size in sizes]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # График энтропии
    ax1.set_xlabel('Размер блока (байт)')
    ax1.set_ylabel('Энтропия (бит/байт)', color='tab:blue')
    ax1.plot(sizes, entropies, 'bo-', label='Энтропия')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(True)

    # График коэффициента сжатия
    ax2 = ax1.twinx()
    ax2.set_ylabel('Коэффициент сжатия', color='tab:red')
    ax2.plot(sizes, ratios, 'rs--', label='Сжатие')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('Энтропия и коэффициент сжатия BWT+MTF')
    fig.tight_layout()
    plt.show()

# Обновленный пример использования
if __name__ == "__main__":
    with open('D:\Pycharm projects\Help Natasha\enwik7.txt', 'rb') as f:
        test_data = f.read(1024 * 1024)  # Первый мегабайт

    results = analyze_compression(test_data)
    print_results_table(results)
    plot_combined_results(results)
