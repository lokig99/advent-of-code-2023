from dataclasses import dataclass


class Tile:
    GROUND = '.'
    VERTICAL = '|'
    HORIZONTAL = '-'
    BEND_NORTH_EAST = 'L'
    BEND_NORTH_WEST = 'J'
    BEND_SOUTH_WEST = '7'
    BEND_SOUTH_EAST = 'F'
    STARTING_POSITION = 'S'


class Direction:
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

    @staticmethod
    def list() -> list[str]:
        return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    @staticmethod
    def opposite(direction: str) -> str:
        match direction:
            case Direction.UP:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.UP
            case Direction.LEFT:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.LEFT


POSSIBLE_CONNECTIONS_FOR_DIRECTION = {
    Direction.UP: [Tile.VERTICAL, Tile.BEND_SOUTH_EAST, Tile.BEND_SOUTH_WEST],
    Direction.DOWN: [Tile.VERTICAL, Tile.BEND_NORTH_EAST, Tile.BEND_NORTH_WEST],
    Direction.RIGHT: [Tile.HORIZONTAL, Tile.BEND_NORTH_WEST, Tile.BEND_SOUTH_WEST],
    Direction.LEFT: [Tile.HORIZONTAL,
                     Tile.BEND_NORTH_EAST, Tile.BEND_SOUTH_EAST]
}


PIPE_POSSIBLE_DIRECTIONS: dict[str, set[str]] = {
    Tile.VERTICAL: {Direction.UP, Direction.DOWN},
    Tile.HORIZONTAL: {Direction.RIGHT, Direction.LEFT},
    Tile.BEND_NORTH_EAST: {Direction.UP, Direction.RIGHT},
    Tile.BEND_NORTH_WEST: {Direction.UP, Direction.LEFT},
    Tile.BEND_SOUTH_EAST: {Direction.DOWN, Direction.RIGHT},
    Tile.BEND_SOUTH_WEST: {Direction.DOWN, Direction.LEFT},
    Tile.GROUND: {},
    Tile.STARTING_POSITION: {}
}


class Node:
    def __init__(self, type: str, position: tuple[int, int], sketch_height: int, sketch_width: int) -> None:
        self.type: str = type
        self.px, self.py = position

        self.__input: 'Node' = None
        self.__output: 'Node' = None
        self.__distance = 0

        self.left: tuple[int, int] = None
        self.right: tuple[int, int] = None
        self.top: tuple[int, int] = None
        self.bottom: tuple[int, int] = None

        self.__possible_directions = PIPE_POSSIBLE_DIRECTIONS[self.type]
        # self.__possible_connections = {
        #     d: POSSIBLE_CONNECTIONS_FOR_DIRECTION[d] for d in POSSIBLE_CONNECTIONS_FOR_DIRECTION if d in self.__possible_directions}

        self.__calculate_neighbours_positions(sketch_height, sketch_width)

    @property
    def distance(self):
        return self.__distance

    @property
    def input(self):
        return self.__input

    @input.setter
    def input(self, value: 'Node'):
        self.__input = value
        self.__distance = value.distance + 1

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, next: 'Node'):
        self.__output = next
        next.input = self

    def __input_direction(self) -> str | None:
        if not self.input:
            return None
        dx = self.px - self.input.px
        dy = self.py - self.input.py

        if dx == -1:
            return Direction.LEFT
        if dx == 1:
            return Direction.RIGHT
        if dy == -1:
            return Direction.UP
        return Direction.DOWN

    def __output_direction(self) -> str | None:
        input_dir = self.__input_direction()
        if not input_dir:
            return None
        return self.__possible_directions.difference([Direction.opposite(input_dir)]).pop()

    def find_next(self, sketch: list[list['Node']]) -> 'Node':
        direction = self.__output_direction()
        match direction:
            case Direction.UP:
                x, y = self.top
            case Direction.DOWN:
                x, y = self.bottom
            case Direction.LEFT:
                x, y = self.left
            case Direction.RIGHT:
                x, y = self.right
        node = sketch[y][x]
        self.output = node
        return node

    def __calculate_neighbours_positions(self, sketch_height: int, sketch_width: int) -> None:
        for direction in Direction.list():
            match direction:
                case Direction.UP:
                    if self.py == 0:
                        continue
                    self.top = self.px, self.py - 1
                case Direction.DOWN:
                    if self.py + 1 == sketch_height:
                        continue
                    self.bottom = self.px, self.py + 1
                case Direction.LEFT:
                    if self.px == 0:
                        continue
                    self.left = self.px - 1, self.py
                case Direction.RIGHT:
                    if self.px + 1 == sketch_width:
                        continue
                    self.right = self.px + 1, self.py

    def __str__(self) -> str:
        return f'{self.type}'

    def __repr__(self) -> str:
        return str(self)


def load_sketch(filepath: str) -> list[list[Node]]:
    with open(filepath, mode='rt') as file:
        sketch = []
        lines = file.readlines()
        height = len(lines)
        width = len(lines[0].strip())
        for y, line in enumerate(lines):
            nodes = []
            for x, ch in enumerate(line.strip()):
                nodes.append(Node(ch, (x, y), height, width))
            sketch.append(nodes)
        return sketch


def sketch_to_string(sketch: list[list[Node]], only_loop=False, distances=False) -> str:
    output = ''
    for nodes in sketch:
        tiles = []
        for node in nodes:
            if only_loop:
                if node.input or node.output or node.type == Tile.STARTING_POSITION:
                    if distances:
                        tiles.append(str(node.distance))
                    else:
                        tiles.append(node.type)
                else:
                    tiles.append(Tile.GROUND)
            else:
                tiles.append(node.type)
        output = f'{output}{''.join(tiles)}\n'
    return output[:-1]


@dataclass
class Loop:
    starting_node: Node
    output_first: Node
    output_second: Node
    farthest_node: Node
    sketch: list[list[Node]]
    
    def to_string_non_loop(self) -> str:
        output = ''
        for nodes in sketch:
            tiles = []
            for node in nodes:
                if node.input or node.output or node.type == Tile.STARTING_POSITION:
                    tiles.append(Tile.GROUND)
                else:
                    tiles.append(node.type)
            output = f'{output}{''.join(tiles)}\n'
        return output[:-1]       


def find_loop(sketch: list[list[Node]]) -> Loop:
    def find_loop_input_nodes(start: Node) -> tuple[Node, Node]:
        possible_nodes = []
        for direction in Direction.list():
            x, y = -1, -1
            match direction:
                case Direction.UP:
                    if start.top:
                        x, y = start.top
                case Direction.DOWN:
                    if start.bottom:
                        x, y = start.bottom
                case Direction.LEFT:
                    if start.left:
                        x, y = start.left
                case Direction.RIGHT:
                    if start.right:
                        x, y = start.right
            if x < 0:
                continue
            node = sketch[y][x]
            if node.type != Tile.GROUND and Direction.opposite(direction) in PIPE_POSSIBLE_DIRECTIONS[node.type]:
                possible_nodes.append(node)

        if len(possible_nodes) > 2:
            raise ValueError(f'Ooooops! Should find only two possible nodes! Found: {
                             len(possible_nodes)}')

        path1_start, path2_start = possible_nodes[0], possible_nodes[1]
        path1_start.input = start
        path2_start.input = start
        return path1_start, path2_start

    nodes = [n for nodes in sketch for n in nodes]
    starting_node = [n for n in nodes if n.type == Tile.STARTING_POSITION][0]
    path1_start, path2_start = find_loop_input_nodes(starting_node)

    path1_current = path1_start
    path2_current = path2_start
    while path1_current != path2_current:
        path1_current = path1_current.find_next(sketch)
        path2_current = path2_current.find_next(sketch)
        
    loop = Loop(starting_node, path1_start, path2_start, path1_current, sketch)
    return loop


if __name__ == '__main__':
    sketch = load_sketch('input.txt')

    loop = find_loop(sketch)
  #  print(sketch_to_string(sketch, only_loop=False))
    print()
    print(sketch_to_string(sketch, only_loop=True))
    print()
  #  print(sketch_to_string(sketch, only_loop=True, distances=True))
    print()
    print('STEPS ALONG THE LOOP TO THE FARTHEST POINT FROM START:\n', loop.farthest_node.distance)
    print()
    print(loop.to_string_non_loop())
