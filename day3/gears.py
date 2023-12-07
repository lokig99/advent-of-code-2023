import sys


class Number:
    def __init__(self, value: int, position: tuple[int, int]) -> None:
        self.value = value
        self.position = position
        self.isserial = False

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'{{{self.value}, {self.position}}}'

    def in_zone(self, symbol: 'Symbol', mark_if_true=False) -> bool:
        l, c = self.position
        symbol_l, symbol_c = symbol.position
        number_len = len(str(self.value))
        start = c - 1
        end = start + number_len + 1

        def test_vertical() -> bool:
            return symbol_c >= start and symbol_c <= end

        def test_horizontal(h_index) -> bool:
            return h_index >= 0 and symbol_l == h_index

        def test_top() -> bool:
            return test_horizontal(l - 1)

        def test_inline() -> bool:
            return test_horizontal(l)

        def test_bottom() -> bool:
            return test_horizontal(l + 1)

        result = test_vertical() and (test_top() or test_inline() or test_bottom())
        if mark_if_true and result:
            self.isserial = True
        return result


class Symbol:
    def __init__(self, value: str, position: tuple[int, int]) -> None:
        self.position = position
        self.value = value
        self.serials: set[Number] = set()

    @property
    def isgear(self) -> bool:
        return self.value == '*' and len(self.serials) == 2

    def add_serial(self, serial: Number):
        self.serials.add(serial)

    @property
    def gear_ratio(self) -> int:
        if not self.isgear:
            return 0
        serials = list(self.serials)
        return serials[0].value * serials[1].value


class Schematic:
    def __init__(self, width: int, height: int, numbers: list[Number], symbols: list[Symbol]) -> None:
        self.width = width
        self.height = height
        self.numbers = numbers
        self.symbols = symbols

        self.gnumbers = self.group_numbers()
        self.gsymbols = self.group_symbols()

        self.__mark_serials()

    def __str__(self) -> str:
        return f'Schematic(width={self.width}, height={self.height}, number={self.numbers}, symbols={self.symbols})'

    def __mark_serials(self):
        for symbol in self.symbols:
            sx, _ = symbol.position
            start = sx - 1
            end = sx + 1

            numbers: list[Number] = []
            if start >= 0:
                numbers.extend(self.gnumbers[start])

            numbers.extend(self.gnumbers[sx])

            if end < self.height:
                numbers.extend(self.gnumbers[end])

            for number in numbers:
                if number.in_zone(symbol, mark_if_true=True):
                    symbol.add_serial(number)

    @staticmethod
    def from_file(filepath: str) -> 'Schematic':
        numbers = []
        symbols = []

        def parse_line(line: str, line_index: int) -> None:
            buffer = ''
            position = -1
            for i, ch in enumerate(line.strip()):
                if ch.isnumeric():
                    if not buffer:
                        position = i
                    buffer = f'{buffer}{ch}'
                else:
                    if buffer:
                        number = Number(int(buffer), (line_index, position))
                        numbers.append(number)
                        buffer = ''
                    if ch != '.':
                        symbol = Symbol(ch, (line_index, i))
                        symbols.append(symbol)
            if buffer:
                number = Number(int(buffer), (line_index, position))
                numbers.append(number)

        with open(filepath, mode='rt') as file:
            lines = file.readlines()
            width = len(lines[0].strip())
            height = len(lines)
            for i, line in enumerate(lines):
                parse_line(line, i)

            return Schematic(width, height, numbers, symbols)

    @property
    def serials(self) -> list[int]:
        return [n.value for n in self.numbers if n.isserial]

    def group_numbers(self) -> list[list[Number]]:
        grouped_numbers: list[list[Number]] = []
        for _ in range(self.height):
            grouped_numbers.append([])
        for number in self.numbers:
            x, _ = number.position
            grouped_numbers[x].append(number)
        return grouped_numbers

    def group_symbols(self) -> list[list[Symbol]]:
        grouped_symbols = []
        for _ in range(self.height):
            grouped_symbols.append([])
        for symbol in self.symbols:
            x, _ = symbol.position
            grouped_symbols[x].append(symbol)
        return grouped_symbols

    def generate_matrix(self, include_serials=True) -> str:
        lines = []
        for h in range(self.height):
            line = ['.' for _ in range(self.width)]
            # populate symbols
            for s in self.gsymbols[h]:
                _, sy = s.position
                line[sy] = s.value
            # populate numbers
            for n in self.gnumbers[h]:
                if not include_serials and n.isserial:
                    continue
                _, ny = n.position
                for i, digit in enumerate(str(n.value)):
                    line[ny+i] = digit

            lines.append(''.join(line))

        return '\n'.join(lines)

    @property
    def gears(self) -> list[Symbol]:
        gears = []
        for s in self.symbols:
            if s.isgear:
                gears.append(s)
        return gears


if __name__ == '__main__':
    path = sys.argv[1]
    schema = Schematic.from_file(path)

    # print(schema)

    # print(schema.serials)

    # print('\n\n')

    # for group in schema.group_numbers():
    #     print(group)

    # print('\n\n')

    # for group in schema.group_symbols():
    #     print(group)

    # print('\n\n')

    print('SUM OF SERIALS:', sum(schema.serials))
    print('SUM OF GEAR POWERS:', sum((g.gear_ratio for g in schema.gears)))

    print('\n\n')

    print(schema.generate_matrix(include_serials=True))
