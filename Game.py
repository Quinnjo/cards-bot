# The Game object is what the discord part of the bot will use to run the game
from GameObjects import Player, Card, Prompt
import random

class Game:
    def __init__(self):
        self.players = list()
        self.card_deck = list()
        self.prompt_deck = list()
        self.started = False
    
    def start(self):
        self.started = true

    def add_player(self, player):
        self.players.append(player)

    def remove_player_with_name(self, name):
        for i in range(len(self.players)):
            if name == self.players[i].name:
                self.players.pop(i)
                break
    
    def number_of_players(self):
        return len(self.players)

    # adds the list cards to the card deck
    def add_to_card_deck(self, cards):
        self.card_deck.append(cards)

    def add_to_prompt_deck(self, prompts):
        self.prompt_deck.append(prompts)

    # deals num cards to player, default is 1
    def deal_to(self, player, num = 1):
        for i in range(num):
            player.add_card(self.card_deck.pop())
    
    # deals num cards to all players, default is 1
    def deal_to_all(self, num = 1):
        for player in players:
            self.deal_to(player, num)

    # returns a prompt off the top of the deck
    def deal_prompt(self):
        return self.prompt_deck.pop()

    def shuffle_decks(self):
        random.seed()
        random.shuffle(self.card_deck)
        random.shuffle(self.prompt_deck)

    # returns a string with each player and their score on a line
    def get_score(self):
        score_list = [(player.name, player.points) for player in self.players]
        result = str()
        for tup in score_list:
            result += "{} has score {}\n".format(tup)
        return result
    
    def new_round(self):
        return Round(self.deal_prompt(), self)

# This object models a round of the game
# The card czar chooses from the cards in the list options
class Round:
    def __init__(self, prompt, game):
        self.prompt = prompt
        self.played_cards = list()
        self.game = game
    
    def add_to_played_cards(self, card):
        self.played_cards.append(card)

    # def choose_card(self, card):

    def shuffle_played_cards(self):
        random.seed()
        random.shuffle(self.played_cards)

    # returns true if every player (minus the judge) has played a card
    def is_ready(self):
        return len(self.get_played_cards) == len(game.players) - 1
    
    def get_played_cards(self):
        return self.played_cards