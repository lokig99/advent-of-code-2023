from math import sqrt, ceil


class Race:
    def __init__(self, time: int, record_distance: int) -> None:
        self.time = time
        self.record_distance = record_distance

    def distance(self, holding_time: int) -> int:
        return -holding_time**2 + holding_time*self.time

    def possible_ways(self) -> int:
        # holding_time = x
        # time = T
        # distance = -x^2 + xT

        delta = self.time**2 - 4 * self.record_distance

        if delta > 0:
            x1 = ceil((self.time - sqrt(delta)) / 2)
            x2 = int((self.time + sqrt(delta)) / 2)

            ways = int(x2 - x1)

            if self.distance(x1) > self.record_distance:
                ways += 1

            if self.distance(x2) <= self.record_distance:
                ways -= 1

            return ways
        return 0


def load_races_from_file(filepath: str) -> list[Race]:
    with open(filepath, mode='rt') as file:
        time_line, distance_line = file.read().strip().splitlines()
        times = (int(t) for t in time_line.split()[1:])
        distances = [int(d) for d in distance_line.split()[1:]]

        races = []
        for i, time in enumerate(times):
            race = Race(time, distances[i])
            races.append(race)

        return races


def load_one_long_race(filepath: str) -> Race:
    with open(filepath, mode='rt') as file:
        time_line, distance_line = file.read().strip().splitlines()
        time = ''.join((t for t in time_line.split()[1:]))
        distance = ''.join((d for d in distance_line.split()[1:]))
        return Race(int(time), int(distance))


def number_of_ways(races: list[Race]) -> int:
    ways = races[0].possible_ways()
    for race in races[1:]:
        ways *= race.possible_ways()
    return ways


if __name__ == '__main__':
    filepath = 'input.txt'

    races = load_races_from_file(filepath)
    print(number_of_ways(races))

    longrace = load_one_long_race(filepath)
    print(longrace.possible_ways())
