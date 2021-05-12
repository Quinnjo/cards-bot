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
    await game.start()
    await ctx.send("Started a new game. Type $join to join! Load one or more decks with $load. Once all the players have joined, use $begin.")
    
@bot.command()
async def join(ctx):
    user = ctx.author
    new_player = Player(user)
    await game.add_player(new_player)
    await player_dict.update(user, new_player)
    await ctx.send("{} was added to the game.".format(new_player.name))

@bot.command()
async def load(ctx, *keys):
    for key in keys:
        await game.add_to_card_deck(get_all_playing_cards(key))
        await game.add_to_prompt_deck(get_all_prompt_cards(key))
        await ctx.send("{} loaded".format(key))

@bot.command()
async def begin(ctx):
    if game.number_of_players() < 3:
        ctx.send('Need at least 3 players')
        return

    msg = await ctx.send("Shuffling")
    await game.shuffle_decks()
    
    # Deal x cards to each player
    msg.edit("Dealing")
    await game.deal_to_all(CARDS_PER_HAND)

    round_number = 1
    # Continue to loop this until one player wins
    while not any([player.points >= ROUNDS_TO_WIN for player in game.players]):
        # make a new round with a new judge
        current_round = game.new_round()
        current_judge = game.players[(round_number - 1) % game.number_of_players()] # picks the judge based off of the round number
        winning_card = None

        # send each player all of their cards
        await send_cards()
        # wait for each player to select a card
        try:
            await asyncio.wait_for(all_cards_played(), timeout=120.0) # Players have 2 minutes to pick a card
        except asyncio.TimeoutError:
            await ctx.send("One or more players didn't turn in a card. Continuing anyways")
        # shuffle the played cards
        current_round.shuffle_played_cards()
        # send these cards to the judge
        await send_cards_to_judge()
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
        # advance to the next round
        round_number += 1
    
    # Declare Winner

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

@bot.command()
@commands.check(is_judge) # only allow if the user is the judge
async def judge(ctx, number):
    if not isinstance(number, int):
        ctx.send('Please use $judge with the *number* of your desired card')
    elif not 1 <= number <= len(current_round.played_cards):
        ctx.send('Pick a number that corresponds to a card')
    else:
        winning_card = current_round.played_cards[number - 1]


    

@bot.command()
async def pick(ctx, number):
    # Get the player object for this user
    try:
        player = player_dict[ctx.author]
    except KeyError:
        ctx.send('You are not a player in this game!')

    if not isinstance(number, int):
        ctx.send('Please use $pick with the *number* of your desired card')
    elif not 1 <= number <= len(player.hand):
        ctx.send('Pick a number that corresponds to a card')
    else:
        current_round.add_to_played_cards(player.play_card(player.hand[number - 1]))


async def send_cards():
    def craft_embed(player):
        embed = discord.Embed(title='$pick one of your cards')
        
        # build a string for cards
        string_of_cards = ''
        for i in range(len(player.hand)):
            card = player.hand[i]
            string_of_cards += '{}. {}\n'.format(i + 1, str(card))

        # return an embed with all of the cards
        return embed.add_field(string_of_cards)
    
    # send each player a unique embed
    for player in game.players:
        await player.user.send(craft_embed(player))

async def send_cards_to_judge():
    embed = discord.Embed(title='$judge one of these cards')

    string_of_cards = ''
    for i in range(len(current_round.played_cards)):
        string_of_cards += '{}. {}\n'.format(i + 1, str(current_round.played_cards[i]))
    
    await current_judge.user.send(embed)

