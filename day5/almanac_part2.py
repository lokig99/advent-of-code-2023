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
    def __init__(self, start: int, length: int) -> None:
        self.start = start
        self.end = start + length - 1

        if self.start > self.end:
            raise ValueError(f"Start cannot be larger than End: {self}")

    @staticmethod
    def from_startend(start, end) -> 'Range':
        return Range(start, end - start + 1)

    def __str__(self) -> str:
        return f'Range(start={self.start}, end={self.end})'

    def __repr__(self) -> str:
        return str(self)

    def diff(self, other: 'Range') -> list['Range']:
        if other.end < self.start or other.start > self.end:
            return [Range.from_startend(other.start, other.end)]
        if other.start >= self.start and other.end > self.end:
            return [Range.from_startend(self.end + 1, other.end)]
        if other.end >= self.start and other.start < self.start:
            range_outside = Range.from_startend(
                other.start, self.start - 1)
            ranges = [range_outside]
            if other.end > self.end:
                range_outside2 = Range.from_startend(
                    self.end + 1, other.end)
                ranges.append(range_outside2)
            return ranges

    def intersect(self, other: 'Range') -> 'Range':
        if other.start <= self.start:
            if other.end >= self.end:
                return Range.from_startend(self.start, self.end)
            if other.end < self.end and other.end >= self.start:
                return Range.from_startend(self.start, other.end)
        if other.start > self.start and other.start <= self.end:
            if other.end >= self.end:
                return Range.from_startend(other.start, self.end)
            if other.end < self.end:
                return Range.from_startend(other.start, other.end)
        return None


class MappingRange:
    def __init__(self, dest_start: int, src_start: int, range_len: int) -> None:
        self.src_range = Range(src_start, range_len)
        self.dest_start = dest_start

    def in_range(self, source_value: int) -> bool:
        return source_value >= self.src_range.start and source_value <= self.src_range.end

    def get(self, source_value: int) -> int | None:
        if not self.in_range(source_value):
            return None
        diff = source_value - self.src_range.start
        return self.dest_start + diff

    def get_from_range(self, source_range: Range) -> tuple[list[Range], Range | None]:
        mapped_range = None
        ranges_outside = self.src_range.diff(source_range)
        range_inside = self.src_range.intersect(source_range)
        if range_inside:
            mapped_start = self.get(range_inside.start)
            mapped_end = self.get(range_inside.end)
            mapped_range = Range.from_startend(mapped_start, mapped_end)
        return ranges_outside, mapped_range


class Map:
    def __init__(self) -> None:
        self.__implicit_ranges: list[MappingRange] = []

    def add(self, dest_range_start: int, source_range_start: int, range_len: int) -> 'Map':
        range = MappingRange(dest_range_start, source_range_start, range_len)
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

    def get_from_range(self, source_range: Range) -> list[Range]:
        results: list[Range] = []

        def map_range(src_range, mapping_range: MappingRange) -> list[Range]:
            unmapped, mapped = mapping_range.get_from_range(src_range)
            if mapped:
                results.append(mapped)
            return unmapped

        queue: list[Range] = [source_range]
        new_queue: list[Range] = []
        for range in self.__implicit_ranges:
            while queue:
                unmapped_range = queue.pop()
                new_unmapped = map_range(unmapped_range, range)
                if new_unmapped:
                    new_queue.extend(new_unmapped)
            queue = new_queue[:]
            new_queue = []

        results.extend(queue)
        return results

    def __str__(self) -> str:
        return f'Map(implicit_mappings={self.__implicit_ranges})'

    def __repr__(self) -> str:
        return str(self)


def load_data(filepath: str, ) -> tuple[list[Range], dict[int, Map]]:
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
        seed_ranges = []
        for i, seed in enumerate(seeds):
            if i % 2 == 0:
                seed_ranges.append(Range(seed, seeds[i+1]))

        maps = {}
        for index in range(1, FieldIndex.LOCATION + 1):
            maps[index] = parse_map_field(fields[index])

        return seed_ranges, maps


def find_location(maps: dict[int, Map], seed: int) -> int:
    seed_to_soil = maps[FieldIndex.SOIL].get(seed)
    soil_to_fertilizer = maps[FieldIndex.FERTILIZER].get(seed_to_soil)
    fertilizer_to_water = maps[FieldIndex.WATER].get(soil_to_fertilizer)
    water_to_light = maps[FieldIndex.LIGHT].get(fertilizer_to_water)
    light_to_temp = maps[FieldIndex.TEMPERATURE].get(water_to_light)
    temp_to_humidity = maps[FieldIndex.HUMIDITY].get(light_to_temp)
    humidity_to_location = maps[FieldIndex.LOCATION].get(temp_to_humidity)
    return humidity_to_location


def process_ranges(ranges: list[Range], map: Map) -> list[Range]:
    results = []
    for range in ranges:
        result = map.get_from_range(range)
        results.extend(result)
    return results


def find_location_from_ranges(maps: dict[int, Map], seeds: list[Range]) -> list[Range]:
    seed_to_soil = process_ranges(seeds, maps[FieldIndex.SOIL])
    soil_to_fertilizer = process_ranges(
        seed_to_soil, maps[FieldIndex.FERTILIZER])
    fertilizer_to_water = process_ranges(
        soil_to_fertilizer, maps[FieldIndex.WATER])
    water_to_light = process_ranges(
        fertilizer_to_water, maps[FieldIndex.LIGHT])
    light_to_temp = process_ranges(
        water_to_light, maps[FieldIndex.TEMPERATURE])
    temp_to_humidity = process_ranges(light_to_temp, maps[FieldIndex.HUMIDITY])
    humidity_to_location = process_ranges(
        temp_to_humidity, maps[FieldIndex.LOCATION])
    return humidity_to_location


if __name__ == '__main__':
    seeds, maps = load_data('input.txt')

    locations = find_location_from_ranges(maps, seeds)

    min_location = min(locations, key=lambda range: range.start)

    print(locations)
    print("SMALLEST LOCATION:", min_location.start)
