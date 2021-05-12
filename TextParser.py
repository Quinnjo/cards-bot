from GameObjects import Card, Prompt

PLAYING_CARD_DICT = {'default':'cards/white.txt','test':'cards/test_cards.txt'}
PROMPT_CARD_DICT = {'default':'cards/black.txt','test':'cards/test_prompts.txt'}
BLANK_STRING = '[blank]'
JUDGE_STRING = '[judge]'

# parses the text file given by the key
# returns a list of cards
def get_all_playing_cards(key):
    with open(PLAYING_CARD_DICT[key]) as file:
        card_strings = file.readlines() # reads every line of the file, returns a list of strings
        list_of_cards = list()
        for card in card_strings:
            list_of_cards.append(Card(card))
        return list_of_cards

# parses the text file given by the key
# returns a list of cards
def get_all_prompt_cards(key):
    with open(PROMPT_CARD_DICT[key]) as file:
        card_strings = file.readlines()
        list_of_prompts = list()
        for prompt in card_strings:
            num_blanks = prompt.split(' ').count(BLANK_STRING) # counts the number of blanks
            has_judge = JUDGE_STRING in prompt
            list_of_prompts.append(Prompt(prompt, num_blanks, has_judge))
        return list_of_prompts

# TESTING
if __name__ == '__main__':
    cards = get_all_playing_cards('default')
    prompts = get_all_prompt_cards('default')
    for card in cards: print(card)
    for prompt in prompts: print(prompt)
