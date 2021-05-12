import discord
from discord.ext import commands
from Game import Game, Round
from GameObjects import Player, Card, Prompt
from TextParser import get_all_playing_cards, get_all_prompt_cards
import asyncio

PREFIX = '$'
CARDS_PER_HAND =  3
ROUNDS_TO_WIN = 5

bot = commands.Bot(command_prefix=PREFIX)

game = Game() # The game object that will be used
current_round = None
current_judge = None
winning_card = None
player_dict = dict() # A dictionary, User:Player

@bot.command()
async def ping(ctx):
    await ctx.reply('pong!')

@bot.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.send(':wave:')
    await ctx.bot.close()

@bot.command()
async def newgame(ctx):
    game.start()
    await ctx.send("Started a new game. Type $join to join! Load one or more decks with $load. Once all the players have joined, use $begin.")
    
@bot.command()
async def join(ctx):
    user = ctx.author # Get the user
    new_player = Player(user) # Convert to a Player object
    game.add_player(new_player) # Add this player to the game
    player_dict[user] = new_player # Add this User:Player pair to the dictionary
    await ctx.send("{} was added to the game.".format(new_player.name))

@bot.command()
async def load(ctx, *keys):
    for key in keys:
        game.add_to_card_deck(get_all_playing_cards(key))
        game.add_to_prompt_deck(get_all_prompt_cards(key))
        await ctx.send("{} loaded".format(key))

# Sends stats related to the game
# Right now, sends the number of cards and prompts
@bot.command()
async def stats(ctx):
    await ctx.send(f'Number of cards: {len(game.card_deck)}\nNumber of prompts: {len(game.prompt_deck)}')

# Command to begin the game
@bot.command()
async def begin(ctx):
    if game.number_of_players() < 3:
        await ctx.send('Need at least 3 players')
        return

    if len(game.card_deck) ==  0 or len(game.prompt_deck) == 0:
        await ctx.send('You need to load one or more decks!')
        return

    msg = await ctx.send("Shuffling")
    game.shuffle_decks()
    
    # Deal x cards to each player
    msg.edit("Dealing")
    game.deal_to_all(CARDS_PER_HAND)

    round_number = 0
    # Continue to loop this until one player wins
    while not any([player.points >= ROUNDS_TO_WIN for player in game.players]):
        # make a new round with a new judge
        round_number += 1
        current_round = game.new_round()
        current_judge = game.players[(round_number - 1) % game.number_of_players()] # picks the judge based off of the round number
        winning_card = None

        await ctx.send(f'Round {round_number}:')
        await ctx.send(f'The judge is {current_judge.name}!')
        await ctx.send(f'Sending each player their cards')

        # send each player all of their cards
        await send_cards()

        # wait for each player to select a card
        try:
            await asyncio.wait_for(all_cards_played(), timeout=120.0) # Players have 2 minutes to pick a card
        except asyncio.TimeoutError:
            await ctx.send("One or more players didn't turn in a card. Continuing anyways")
        
        # shuffle the played cards
        current_round.shuffle_played_cards()
        
        # send these cards to the judge with ctx
        await send_cards_to_judge(ctx)
        
        # wait for the judge to make a choice
        try:
            await asyncio.wait_for(judge_has_chosen(), timeout=180.0) # The judge has 3 minutes to pick a card
        except asyncio.TimeoutError:
            await ctx.send("The judge did not choose a card")
            continue
        
        # award points
        await ctx.send('The winning card is {}, played by {}'.format(str(winning_card), winning_card.holder.name))
        winning_card.holder.add_point()
        
        # show the score
        await ctx.send(build_score_embed())
        
        # deal cards to each player
        for player in game.players:
            if player is not current_judge:
                game.deal_to(player, num=current_round.prompt.num_blanks)
        
        # advance to the next round
    
    # TODO: Declare Winner

async def build_score_embed():
    embed = discord.Embed(title='Score')
    score_string = ''
    for player in game.players:
        score_string += '{} - {}\n'.format(str(player), player.points)
    return embed.add_field(score_string)

async def all_cards_played():
    while not current_round.is_ready():
        await asyncio.sleep(5)
    return True

async def judge_has_chosen():
    while not winning_card:
        await asyncio.sleep(5)
    return True

async def is_judge(ctx):
    return ctx.author == current_judge

# Command the judge uses to pick a winning card
@bot.command()
@commands.check(is_judge) # only allow if the user is the judge
async def judge(ctx, number):
    if not isinstance(number, int):
        await ctx.send('Please use $judge with the *number* of your desired submission')
        return
    elif not 1 <= number <= len(current_round.played_cards):
        await ctx.send('Pick a number that corresponds to a submission')
        return
    else:
        winning_card = current_round.played_cards[number - 1]

@bot.command()
async def pick(ctx, *numbers):
    # Get the player object for this user
    try:
        player = player_dict[ctx.author]
    except KeyError:
        await ctx.send('You are not a player in this game!')
        return

    if len(numbers) != current_round.prompt.num_blanks:
        await ctx.send('Please select the correct number of cards')
        return

    cards_to_play = list() # A list of cards played by this player
    for number in numbers:
        if not isinstance(number, int):
            ctx.send('Please use $pick with the *number(s)* of your desired card(s)')
        elif not 1 <= number <= len(player.hand):
            ctx.send('Pick a number that corresponds to a card')
        else:
            cards_to_play.append(player.hand[number-1])
    for card in cards_to_play:
        player.play_card(card) # removes the cards from the player's hand
    current_round.add_to_played_cards(cards_to_play) # adds this list of cards to the played cards

async def send_cards():
    def craft_embed(player):
        embed = discord.Embed(title='$pick one (or more) of your cards')
        
        # build a string for cards
        string_of_cards = ''
        for i in range(len(player.hand)):
            card = player.hand[i]
            string_of_cards += '{}. {}\n'.format(i + 1, str(card))

        # return an embed with all of the cards
        return embed.add_field(string_of_cards)
    
    # send each player a unique embed
    for player in game.players:
        if player is not current_judge:
            await player.user.send(craft_embed(player))

async def send_cards_to_judge(ctx):
    embed = discord.Embed(title='$judge one from this list')

    string_of_cards = ''
    for i in range(len(current_round.played_cards)):
        string_of_cards += f'{i+1}. '
        for c in current_round.played_cards[i]:
            string_of_cards += f'{str(c)}...'      
        string_of_cards += '\n'

    embed.add_field(string_of_cards) 
    
    await current_judge.user.send(embed)
    await ctx.send(embed)

