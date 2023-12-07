class Card:
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    T = 'T'
    J = 'J'
    Q = 'Q'
    K = 'K'
    A = 'A'


class TypeStrength:
    FIVE_OF_KIND = 7E10
    FOUR_OF_KIND = 6E10
    FULL_HOUSE = 5E10
    THREE_OF_KIND = 4E10
    TWO_PAIR = 3E10
    ONE_PAIR = 2E10
    HIGH_CARD = 1E10


class Hand:
    STRENGTH = {Card.TWO: 2, Card.THREE: 3, Card.FOUR: 4, Card.FIVE: 5, Card.SIX: 6, Card.SEVEN: 7,
                Card.EIGHT: 8, Card.NINE: 9, Card.T: 10, Card.J: 11, Card.Q: 12, Card.K: 13, Card.A: 14}

    STRENGTH_WITH_JOKER = {Card.J: 1, Card.TWO: 2, Card.THREE: 3, Card.FOUR: 4, Card.FIVE: 5, Card.SIX: 6, Card.SEVEN: 7,
                           Card.EIGHT: 8, Card.NINE: 9, Card.T: 10,  Card.Q: 11, Card.K: 12, Card.A: 13}

    def __init__(self, cards: list[str], bid: int, joker=False) -> None:
        self.joker = joker
        self.cards: list[str] = cards
        self.bid: int = bid

        self.power: float = self.__calculate_power()

    def __count_cards(self) -> dict[str, int]:
        card_count: dict[str, int] = {}
        for card in self.cards:
            if card in card_count:
                card_count[card] += 1
            else:
                card_count[card] = 1
        return card_count

    def __identify_type(self) -> float:
        card_count = self.__count_cards()
        counts = card_count.values()
        match len(card_count):
            case 1:
                return TypeStrength.FIVE_OF_KIND
            case 2:
                if 4 in counts and 1 in counts:
                    return TypeStrength.FOUR_OF_KIND
                return TypeStrength.FULL_HOUSE
            case 3:
                if 3 in counts:
                    return TypeStrength.THREE_OF_KIND
                return TypeStrength.TWO_PAIR
            case 4:
                return TypeStrength.ONE_PAIR
            case 5:
                return TypeStrength.HIGH_CARD

    def __identify_type_with_jokers(self) -> float:
        card_count = self.__count_cards()
        jokers = 0
        if Card.J in card_count:
            jokers = card_count.pop(Card.J)

        if not jokers:
            return self.__identify_type()

        # max value of `len(counts_without_jokers)` is 4 not 5
        counts_without_jokers = card_count.values()
        match len(counts_without_jokers):
            case 0:  # JJJJJ
                return TypeStrength.FIVE_OF_KIND
            case 1:  # JKKKK or JJKKK or JJJKK or JJJJK
                return TypeStrength.FIVE_OF_KIND
            case 2:  # JKKK2 or JKK22 or JJKK2 or JJJK2
                if jokers == 1:
                    if 3 in counts_without_jokers:
                        return TypeStrength.FOUR_OF_KIND
                    return TypeStrength.FULL_HOUSE
                return TypeStrength.FOUR_OF_KIND
            case 3:  # JKK2T or JJK2T
                return TypeStrength.THREE_OF_KIND
            case 4:  # JK2TA
                return TypeStrength.ONE_PAIR

    def __calculate_power(self) -> float:
        power = self.__identify_type_with_jokers() if self.joker else self.__identify_type()
        strengths = Hand.STRENGTH_WITH_JOKER if self.joker else Hand.STRENGTH
        multiplier = 8
        for i, card in enumerate(self.cards):
            tmp = i * 2
            power += strengths[card] * 10**(multiplier - tmp)
        return power

    def __str__(self) -> str:
        return f'Hand({"".join(self.cards)}, {self.power}, {self.bid})'

    def __repr__(self) -> str:
        return str(self)


def load_hands_from_file(filepath: str, joker=False) -> list[Hand]:
    with open(filepath, mode='rt') as file:
        lines = (l.strip() for l in file.readlines())
        hands = []
        for line in lines:
            cards, bid = line.split()
            hand = Hand([c for c in cards], int(bid), joker)
            hands.append(hand)
        return hands


def get_total_winning(hands: list[Hand], debug_logs=False) -> int:
    winning = 0
    sorted_hands = sorted(hands, key=lambda h: h.power)
    for rank, hand in enumerate(sorted_hands, start=1):
        winning += hand.bid * rank

        if debug_logs:
            print(rank, hand)
    return winning


if __name__ == '__main__':
    filepath = 'input.txt'
    
    hands = load_hands_from_file(filepath)
    winning = get_total_winning(hands)
    print('TOTAL WINNINGS (NO jokers rule):', winning)

    hands_with_jokers = load_hands_from_file(filepath, joker=True)
    winning_jokers = get_total_winning(hands_with_jokers)
    print('TOTAL WINNINGS (WITH jokers rule):', winning_jokers)
