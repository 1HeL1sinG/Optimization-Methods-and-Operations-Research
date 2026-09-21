import argparse
from fractions import Fraction
from pathlib import Path


def read_input(path):
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    except OSError as error:
        raise ValueError(f"не удалось прочитать файл: {error}")

    lines = [line for line in lines if line != ""]
    if not lines:
        raise ValueError("файл пуст")

    try:
        sizes = [int(value) for value in lines[0].split()]
    except ValueError as error:
        raise ValueError("в первой строке должны быть целые числа m и n")
    if len(sizes) != 2:
        raise ValueError("в первой строке нужно указать два числа: m и n")
    row_count, col_count = sizes

    if row_count <= 0 or col_count <= 0:
        raise ValueError("числа m и n должны быть положительными")
    
    if len(lines) != row_count + 3:
        raise ValueError(
            f"ожидалось {row_count + 3} непустых строк, получено {len(lines)}"
        )

    matrix = []
    for line in lines[1 : row_count + 1]:
        try:
            row = [Fraction(value) for value in line.split()]
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError(f"некорректное число в матрице")
        if len(row) != col_count:
            raise ValueError(f"Строки должны быть по {col_count} чисел")
        matrix.append(row)

    try:
        row_bounds = [int(value) for value in lines[row_count + 1].split()]
        col_bounds = [int(value) for value in lines[row_count + 2].split()]
    except ValueError as error:
        raise ValueError("границы диапазонов должны быть целыми числами") from error

    selected_rows = make_range(row_bounds, row_count, "строк")
    selected_cols = make_range(col_bounds, col_count, "столбцов")
    if len(selected_rows) != len(selected_cols):
        raise ValueError("диапазоны строк и столбцов должны иметь одинаковую длину")
    return matrix, selected_rows, selected_cols


def make_range(bounds, limit, name):
    if len(bounds) != 2:
        raise ValueError(f"нужно указать начальную и конечную границы {name}")
    start, end = bounds
    if not 1 <= start <= end <= limit:
        raise ValueError(
            f"границы {name} должны удовлетворять условию 1 <= начало <= конец <= {limit}"
        )
    return list(range(start - 1, end))


def diagonalize_minor(matrix, selected_rows, selected_cols):
    for minor_col, real_col in enumerate(selected_cols):
        pivot_position = None

        for candidate in range(minor_col, len(selected_rows)):
            actual_row = selected_rows[candidate]

            if matrix[actual_row][real_col] != 0:
                pivot_position = candidate
                break

        if pivot_position is None:
            return False

        if pivot_position != minor_col:
            row_a = selected_rows[minor_col]
            row_b = selected_rows[pivot_position]
            matrix[row_a], matrix[row_b] = matrix[row_b], matrix[row_a]

        pivot_row = selected_rows[minor_col]
        pivot = matrix[pivot_row][real_col]
        matrix[pivot_row] = [value / pivot for value in matrix[pivot_row]]

        for row in selected_rows:
            if row == pivot_row:
                continue
            factor = matrix[row][real_col]
            if factor != 0:
                matrix[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(matrix[row], matrix[pivot_row])
                ]
    return True


def format_fraction(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def write_matrix(path, matrix):
    text = "\n".join(" ".join(format_fraction(value) for value in row) for row in matrix)
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="input.txt")
    parser.add_argument("--output", default="output.txt")
    args = parser.parse_args()

    try:
        matrix, selected_rows, selected_cols = read_input(Path(args.input))
        if not diagonalize_minor(matrix, selected_rows, selected_cols):
            print("Ошибка: выбранный минор вырожден; привести его к единичной матрице нельзя.")
            return False
        write_matrix(Path(args.output), matrix)
    except ValueError as error:
        print(f"Ошибка входных данных: {error}")
        return False
    except OSError as error:
        print(f"Ошибка записи результата: {error}")
        return False

    print(f"Готово: результат сохранён в {args.output}")
    return True


if __name__ == "__main__":
    main()
