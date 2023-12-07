import sys


RED = 'red'
GREEN = 'green'
BLUE = 'blue'

GAME_SEP = ':'
DRAW_SEP = ';'
CUBE_SEP = ','


class Bag:
    def __init__(self, red: int, green: int, blue: int) -> None:
        self.red = red
        self.green = green
        self.blue = blue

    def is_possible(self, game: dict[str, int]) -> bool:
        return game[RED] <= self.red and game[GREEN] <= self.green and game[BLUE] <= self.blue


def load_games_from_file(filepath: str) -> list[dict[str, int]]:
    games = []
    with open(filepath, mode='r') as file:
        lines = file.read().strip().splitlines()
        for line in lines:
            game = {RED: 0, GREEN: 0, BLUE: 0}
            draws = line.split(GAME_SEP)[1].split(DRAW_SEP)
            for draw in draws:
                cubes = draw.split(CUBE_SEP)
                for cube in cubes:
                    count, color = cube.strip().split()
                    count = int(count)
                    if game[color] < count:
                        game[color] = count
            games.append(game)
    return games


def get_possible_ids(games: list[dict[str, int]], bag: Bag) -> list[int]:
    ids: list[int] = []
    for id, game in enumerate(games, start=1):
        if bag.is_possible(game):
            ids.append(id)
    return ids


def get_powers(games: list[dict[str, int]]) -> list[int]:
    powers = []
    for game in games:
        power = game[RED] * game[BLUE] * game[GREEN]
        powers.append(power)
    return powers


if __name__ == '__main__':
    path = sys.argv[1]
    games = load_games_from_file(path)
    print(games)
 
    bag = Bag(red=12, green=13, blue=14)

    possible = get_possible_ids(games, bag)

    powers = get_powers(games)

    sum_of_possible = sum(possible)
    sum_of_powers = sum(powers)

    print('Possible ids:', possible)
    print('sum of possible ids:', sum_of_possible)
    print('powers:', powers)
    print('sum of powers:', sum_of_powers)
