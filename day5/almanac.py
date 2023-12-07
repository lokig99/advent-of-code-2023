class FieldIndex:
    SEEDS = 0
    SOIL = 1
    FERTILIZER = 2
    WATER = 3
    LIGHT = 4
    TEMPERATURE = 5
    HUMIDITY = 6
    LOCATION = 7


class Range:
    def __init__(self, dest_start: int, src_start: int, range_len: int) -> None:
        self.src_start = src_start
        self.dest_start = dest_start

        self.src_end = src_start + range_len - 1

    def in_range(self, source_value: int) -> bool:
        return source_value >= self.src_start and source_value <= self.src_end

    def get(self, source_value: int) -> int | None:
        if not self.in_range(source_value):
            return None
        diff = source_value - self.src_start
        return self.dest_start + diff


class Map:
    def __init__(self) -> None:
        self.__implicit_ranges: list[Range] = []

    def add(self, dest_range_start: int, source_range_start: int, range_len: int) -> 'Map':
        range = Range(dest_range_start, source_range_start, range_len)
        self.__implicit_ranges.append(range)

    def get(self, source: int) -> int:
        def check_implicit_ranges() -> int | None:
            for range in self.__implicit_ranges:
                value = range.get(source)
                if value:
                    return value
            return None

        if value := check_implicit_ranges():
            return value
        return source

    def __str__(self) -> str:
        return f'Map(implicit_mappings={self.__implicit_ranges})'

    def __repr__(self) -> str:
        return str(self)


def load_data(filepath: str) -> tuple[list[int], dict[int, Map]]:
    def parse_map_field(field: str) -> Map:
        lines = field.strip().split('\n')[1:]
        map = Map()
        for line in lines:
            dest, src, range_len = line.split()
            map.add(int(dest), int(src), int(range_len))
        return map

    with open(filepath, mode='rt') as file:
        data = file.read()
        fields = data.strip().split('\n\n')
        seeds = fields[FieldIndex.SEEDS].strip().split(':')[1].split()
        seeds = [int(s) for s in seeds]

        maps = {}
        for index in range(1, FieldIndex.LOCATION + 1):
            maps[index] = parse_map_field(fields[index])

        return seeds, maps


def find_location(maps: dict[int, Map], seed: int) -> int:
    seed_to_soil = maps[FieldIndex.SOIL].get(seed)
    soil_to_fertilizer = maps[FieldIndex.FERTILIZER].get(seed_to_soil)
    fertilizer_to_water = maps[FieldIndex.WATER].get(soil_to_fertilizer)
    water_to_light = maps[FieldIndex.LIGHT].get(fertilizer_to_water)
    light_to_temp = maps[FieldIndex.TEMPERATURE].get(water_to_light)
    temp_to_humidity = maps[FieldIndex.HUMIDITY].get(light_to_temp)
    humidity_to_location = maps[FieldIndex.LOCATION].get(temp_to_humidity)
    return humidity_to_location


if __name__ == '__main__':

    ###### PART 1 ######################################
    seeds, maps = load_data('input.txt')

    locations = (find_location(maps, seed) for seed in seeds)
    lowest_location = min(locations)

    print('PART 1 --- LOWEST LOCATION:', lowest_location)
