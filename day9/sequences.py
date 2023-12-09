from collections import deque


def load_sequences(filepath: str) -> list[list[int]]:
    with open(filepath, mode='rt') as file:
        lines = file.readlines()
        sequences = []
        for line in lines:
            numbers = [int(n) for n in line.split()]
            sequences.append(numbers)
        return sequences


def extrapolate(sequence: list[int], backwards=False) -> int:
    if backwards:
        sequence = sequence[::-1]
    
    seqset = set(sequence)
    if len(seqset) == 1:
        return sequence[0]
    del seqset

    new_sequence = []
    queue = deque(sequence[:])
    while len(queue) > 1:
        a = queue.popleft()
        b = queue[0]
        c = b - a
        new_sequence.append(c)

    return sequence[-1] + extrapolate(new_sequence)


def part1():
    sequences = load_sequences('input.txt')
    
    extrapolations = [extrapolate(s) for s in sequences]
    print('SUM OF EXTRAPOLATIONS (PART 1):', sum(extrapolations))
    
def part2():
    sequences = load_sequences('input.txt')
    
    extrapolations = [extrapolate(s, backwards=True) for s in sequences]
    print('SUM OF EXTRAPOLATIONS (PART 2):', sum(extrapolations))  


if __name__ == '__main__':
    part1()
    part2()
