from math import lcm
from dataclasses import dataclass


class Node:
    def __init__(self, name: str) -> None:
        self.name = name
        self.left: 'Node' = None
        self.right: 'Node' = None

    def __str__(self) -> str:
        leftname = self.left.name if self.left else 'None'
        rightname = self.right.name if self.right else 'None'
        return f'{self.name} = ({leftname}, {rightname})'

    def __repr__(self) -> str:
        return str(self)


def load_instructions_and_nodes(filepath: str) -> tuple[str, dict[str, Node]]:
    with open(filepath, mode='rt') as file:
        lines = file.readlines()
        instructions = lines[0].strip()
        nodes_with_children: dict[str, tuple[Node, tuple[str, str]]] = {}
        nodes = {}
        for line in lines[2:]:
            name, child_nodes = line.split('=')
            left, right = child_nodes.strip().removeprefix('(').removesuffix(')').split(',')
            node = Node(name.strip())
            nodes_with_children[node.name] = node, [
                left.strip(), right.strip()]

        for node, children_names in nodes_with_children.values():
            left, right = children_names
            node.left = nodes_with_children[left][0]
            node.right = nodes_with_children[right][0]
            nodes[node.name] = node

        return instructions, nodes


def traverse_nodes(instructions: str, nodes: dict[str, Node]) -> int:
    current_node = nodes['AAA']
    steps = 0
    while True:
        for instruction in instructions:
            steps += 1
            match instruction:
                case 'L':
                    current_node = current_node.left
                case 'R':
                    current_node = current_node.right
            if current_node.name == 'ZZZ':
                return steps


class Job:
    def __init__(self, node: Node, instructions: str) -> None:
        self.node = node
        self.instructions = instructions
        self.current_instruction_index = -1
        self.steps = 0

    @staticmethod
    def from_result(result: 'JobResult') -> 'Job':
        return Job(result.current_node, result.instructions, result.last_instruction_id, result.steps)

    def to_result(self) -> 'JobResult':
        return JobResult(self.node, self.steps)

    def __move_step(self) -> None:
        self.current_instruction_index = (
            self.current_instruction_index + 1) % len(self.instructions)
        instruction = self.instructions[self.current_instruction_index]
        match instruction:
            case 'L':
                self.node = self.node.left
            case 'R':
                self.node = self.node.right
        self.steps += 1

    def __ends_with_z(self) -> bool:
        return self.node.name[-1] == 'Z'

    def run(self) -> 'JobResult':
        while True:
            self.__move_step()
            if self.__ends_with_z():
                return self.to_result()


@dataclass
class JobResult:
    current_node: Node
    steps: int


def traverse_nodes_part2(instructions: str, nodes: dict[str, Node]) -> int:
    def find_lcm(results: list[JobResult]) -> int:
        numbers = [r.steps for r in results]
        while len(numbers) > 1:
            a = numbers.pop()
            b = numbers.pop()
            c = lcm(a, b)
            numbers.append(c)
        return numbers[0]

    starting_nodes = [n for n in nodes.values() if n.name[-1] == 'A']
    jobs = (Job(n, instructions) for n in starting_nodes)
    results = []

    for job in jobs:
        results.append(job.run())
    return find_lcm(results)


def part1():
    instructions, nodes = load_instructions_and_nodes('input.txt')
    steps = traverse_nodes(instructions, nodes)

    print('PART1 - STEPS:', steps)


def part2():
    instructions, nodes = load_instructions_and_nodes('input.txt')
    steps = traverse_nodes_part2(instructions, nodes)

    print('PART2 - STEPS:', steps)


if __name__ == '__main__':
    part1()
    part2()
