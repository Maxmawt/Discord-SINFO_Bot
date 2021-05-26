# created by Sami Bosch on Thursday, 08 November 2018

# This file contains all functions necessary to start up the bot

import logging
import discord
from discord.ext.commands import Bot
from message_parser import init


class IngiBot(Bot):
    async def on_command(self, context):
        msg = context.message
        logging.info(f"Received message \"{msg}\", \"{msg.content if hasattr(msg, 'content') else ''}\" to be handled by the bot")


def runbot(token):
    """Initializes the client's command handler and other non command related functionalities."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(funcName)s: %(message)s')
    intents = discord.Intents.default()
    intents.members = True
    client = IngiBot(command_prefix="!", intents=intents)

    init(client)

    client.run(token)
