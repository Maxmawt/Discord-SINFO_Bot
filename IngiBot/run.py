# created by Sami Bosch on Thursday, 08 November 2018

# This file contains all functions necessary to start up the bot

import discord
from discord.ext.commands import Bot
from message_parser import init


def runbot(token):
    """Initializes the client's command handler and other non command related functionalities."""
    intents = discord.Intents.default()
    intents.members = True
    client = Bot(command_prefix="!", intents=intents)

    init(client)

    client.run(token)
