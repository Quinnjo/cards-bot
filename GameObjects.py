# Models a player in the game
class Player:
    # Creates a new player with a Discord user and an optional hand
    def __init__(self, user, hand = list()):
        self.user = user
        self.name = user.display_name
        self.hand = hand
        self.points = 0

    # add a card to the player's hand
    def add_card(self, card):
        card.set_holder(self)
        self.hand.append(card)

    def add_point(self):
        self.points += 1

    def play_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
            return card
        else:
            raise RuntimeError("Can't remove card that doesn't exist")

class Card:
    def __init__(self, text):
        self.text = text
        self.holder = None

    def set_holder(self, player):
        self.holder = player

    def __str__(self):
        return self.text

# Needs a standard character that represents a blank
# If I store all of the cards in a text file, I will need a character/string to represent a blank
class Prompt(Card):
    def __init__(self, prompt, num_blanks):
        self.number_of_blanks = num_blanks
        super().__init__(prompt)
    
    def __str__(self):
        return "Prompt: {}".format(super().__str__())


    

