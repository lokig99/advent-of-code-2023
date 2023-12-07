class Card:
    def __init__(self, winning_numbers: list[str], scratched_numbers: list[str], id: int) -> None:
        self.winning: set[str] = set(winning_numbers)
        self.scratched = scratched_numbers
        self.id = id

        self.matches = self.__getmatches()
        self.score = self.__getscore()

    def __getmatches(self) -> list[str]:
        return self.winning.intersection(self.scratched)

    def __getscore(self) -> int:
        points = 1 if self.matches else 0
        for _ in range(len(self.matches) - 1):
            points *= 2
        return points

    def __str__(self) -> str:
        return f'Card {self.id}: (winning={self.winning} | scratched={self.scratched})'

    def __repr__(self) -> str:
        return str(self)

    def evaluate(self) -> list[int]:
        return [self.id + x + 1 for x, _ in enumerate(self.matches)]


def load_from_file(filepath: str) -> list[Card]:
    def parse_line(line: str, id: int) -> Card:
        _, numbers = line.split(':')
        winning, scratched = numbers.split('|')
        return Card([w for w in winning.strip().split()], [s for s in scratched.strip().split()], id)

    cards = []
    with open(filepath, mode='rt') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            card = parse_line(line, i+1)
            cards.append(card)

    return cards


def process_cards(cards: list[Card]) -> int:
    stack: list[Card] = cards[:]
    deck = {c.id: c for c in cards}
    cards_total = 0

    while stack:
        card = stack.pop()
        cards_total += 1
        copies = card.evaluate()
        for copy in copies:
            if copy in deck:
                stack.append(deck[copy])
    return cards_total


if __name__ == '__main__':
    path = 'input.txt'
    cards = load_from_file(path)
    for card in cards:
        print(card, card.matches, card.score, card.evaluate())

    print('TOTAL SCORE:', sum((c.score for c in cards)))
    print('TOTAL CARDS:', process_cards(cards))
