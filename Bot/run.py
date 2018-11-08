# created by Sami Bosch on Thursday, 08 November 2018

# This file contains all functions necessary to start up the bot

from discord.ext.commands import Bot
from message_parser import init


def runbot(token):
    """Initializes the client's command handler and other non command related functionalities."""
    client = Bot(command_prefix="!")

    init(client)

    client.run(token)
