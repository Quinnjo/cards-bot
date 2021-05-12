import Bot
import logging


# Read the bot token from token.txt
token = ''
with open('token.txt','r') as f:
    token = f.read()

logging.basicConfig(level=logging.INFO)
Bot.bot.run(token)