import sys


def load_data_from_file(filepath: str) -> list[str]:
    with open(filepath, mode='r') as file:
        data = file.read()
        return data.strip().splitlines()


def find_calibration_value(text: str) -> int:
    def get_first_digit(text: str) -> str:
        for ch in text:
            if ch.isdigit():
                return ch
        raise ValueError(f'string: "{text}" does not contain any digits')

    def get_last_digit(text: str) -> str:
        return get_first_digit(text[::-1])

    first, last = get_first_digit(text), get_last_digit(text)
    return int(f'{first}{last}')


if __name__ == '__main__':
    path = sys.argv[1]
    data = load_data_from_file(path)
    sum = 0
    for line in data:
        value = find_calibration_value(line)
        sum += value
        print(line, '->', value)

    print("SUM OF ALL VALUES:", sum)
