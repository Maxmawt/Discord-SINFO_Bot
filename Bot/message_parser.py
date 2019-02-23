# created by Sami Bosch on Thursday, 08 November 2018

# This file contains all functions necessary to reply to messages
import json
import os
import time

import discord
import random
from datetime import date

from discord.ext import commands

from course_handler import create_course, get_courses
from discord_utils import AsyncTimer
from tex_handler import *

haddock = '../haddock.json'
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, haddock)
with open(filename) as f:
    quotes = json.load(f)["quotes"]

bogaert = 'img/bogaert.png'
bogname = os.path.join(dirname, bogaert)

goodenough = 'img/goodenough.png'
goodname = os.path.join(dirname, goodenough)

starttime = time.time()


def init(client):
    class Moderate:
        def __init__(self, bot):
            self.client = bot

        @commands.command(pass_context=True)
        async def ban(self, context):
            """Takes a list of mentioned users + optionally an int. Bans all users in list, and if int has been
            supplied, unbans them after given time in days. """
            m = context.message
            if m.content.find(" ") > 0:
                try:
                    unban_time = float(m.content.split(" ")[-1])
                except ValueError:
                    unban_time = -1
            else:
                unban_time = -1

            if m.author.server_permissions.ban_members:
                for member in m.mentions:
                    await self.client.ban(member, delete_message_days=0)
                    await self.client.say("banned {} for {} days (-1 = indefinite)".format(member.nick, unban_time))

                if unban_time >= 0:
                    async def unban_all():
                        for mem in m.mentions:
                            await self.client.unban(m.server, mem)
                            await self.client.send_message(m.channel, "unbanned {}".format(mem.nick))

                    AsyncTimer(unban_time * 86400, unban_all)
            else:
                await self.client.say("You do not have the permission to ban users")

        @commands.command(pass_context=True)
        async def kick(self, context):
            """Takes a list of mentioned users and kicks them all."""
            m = context.message
            if m.author.server_permissions.kick_members:
                for member in m.mentions:
                    await self.client.kick(member)
                    await self.client.say("kicked {}".format(member.nick))
            else:
                await self.client.say("You do not have the permission to kick users")

        @commands.command(aliases=['mute', 'silence'], pass_context=True)
        async def timeout(self, context):
            """Takes a list of mentioned users and a timeout at the end of the message and silences all users for the
            specified time in minutes."""
            m = context.message
            muted = discord.utils.get(m.server.roles, name='Muted')
            if m.content.find(" ") > 0:
                try:
                    mute_time = float(m.content.split(" ")[-1])
                except ValueError:
                    mute_time = -1
            else:
                mute_time = -1

            if m.author.server_permissions.manage_roles and mute_time >= 0:
                for member in m.mentions:
                    await self.client.add_roles(member, muted)
                    await self.client.say("Muted {} for {} minutes".format(member.nick, int(mute_time)))
                if mute_time >= 0:
                    async def unban_all():
                        for mem in m.mentions:
                            await self.client.remove_roles(mem, muted)
                            await self.client.send_message(m.channel, "Unmuted {}".format(mem.nick))

                    AsyncTimer(mute_time * 60, unban_all)
            elif mute_time == -1:
                await self.client.say("Please provide a time (in minutes)")
            else:
                await self.client.say("You do not have the permission to ban users")

    class Courses:
        def __init__(self, bot):
            self.client = bot

        @commands.command(aliases=['add', 'ac'], pass_context=True)
        async def add_course(self, context):
            """Creates a channel and role for a list of courses."""
            m = context.message
            u = m.author
            if u.server_permissions.manage_channels:
                message = m.content
                if message.find(" ") > 0:
                    for name in message.split(" ")[1:]:
                        role = discord.utils.get(m.server.roles, name=name.upper())
                        if role:
                            await self.client.say("Course exists!")
                        else:
                            await create_course(name, client, m.server)
                            await self.client.say("Created channel and role {}".format(name))
                else:
                    await self.client.say("Please provide a name")
            else:
                await self.client.say("You don't have the permissions to use this command.")

        @commands.command(aliases=['follow', 'fc'], pass_context=True)
        async def follow_course(self, context):
            """Allows an user to follow a list of courses."""
            m = context.message
            u = m.author

            message = m.content
            if message.find(" ") > 0:
                roles = []
                success = ""
                fail = ""
                refused = ""
                for name in message.split(" ")[1:]:
                    role = discord.utils.get(m.server.roles, name=name.upper())
                    if role:
                        annonceur = discord.utils.get(m.server.roles, name="Annonceur")
                        if role >= annonceur or role in u.roles:
                            refused += name + " "
                        else:
                            roles.append(role)
                            success += name + " "
                    else:
                        fail += name + " "
                full = "You successfully followed: " + success.strip() + "\n" if success else ""
                full += "Couldn't follow: " + refused.strip() + "\n" if refused else ""
                full += "Couldn't find: " + fail.strip() if fail else ""
                await self.client.add_roles(u, *roles)
                await self.client.send_message(u, full.strip())
            else:
                await self.client.say("Please provide a course to follow")

        @commands.command(aliases=['unfollow', 'uc'], pass_context=True)
        async def unfollow_course(self, context):
            """Allows an user to unfollow a list of courses."""
            m = context.message
            u = m.author

            message = m.content
            if message.find(" ") > 0:
                roles = []
                success = ""
                fail = ""
                refused = ""
                for name in message.split(" ")[1:]:
                    role = discord.utils.get(m.server.roles, name=name.upper())
                    if role:
                        annonceur = discord.utils.get(m.server.roles, name="Annonceur")
                        if role >= annonceur or role not in u.roles:
                            refused += name + " "
                        else:
                            roles.append(role)
                            success += name + " "
                    else:
                        fail += name + " "
                full = "You successfully unfollowed: " + success.strip() + "\n" if success else ""
                full += "Couldn't unfollow: " + refused.strip() + "\n" if refused else ""
                full += "Couldn't find: " + fail.strip() if fail else ""
                await self.client.remove_roles(u, *roles)
                await self.client.send_message(u, full.strip())
            else:
                await self.client.say("Please provide a course to follow")

        @commands.command(aliases=['list', 'lc'], pass_context=True)
        async def list_courses(self, context):
            """Lists all available courses in the server."""
            courses = get_courses(context.message.server)

            s = "| "
            for course in courses:
                s += course + " | "
            await self.client.say(s.strip())

    class Random:
        def __init__(self, bot):
            self.client = bot

        @commands.command(aliases=['hello', 'hi', "bonjour", "bjr"], pass_context=True)
        async def greetings(self, context):
            """Answer with an hello message"""
            m = context.message
            arg = m.content[m.content.find(" "):].strip()
            if m.content.startswith('!bonjour') or m.content.startswith('!bjr'):
                msg = 'Bonjour {} !'.format(arg)
                # msg = 'Bonjour {0.author.mention} !'.format(m)
            else:
                msg = 'Hello {} !'.format(arg)
            await self.client.say(msg)
            await self.client.delete_message(self, context.message)

        @commands.command(aliases=['haddockquote', 'haddock', 'hq'], pass_context=False)
        async def haddock_says(self):
            """Give a quote from Haddock"""
            msg = random.choice(quotes)
            await self.client.say(msg)

        @commands.command(aliases=['banquet', "date_until_banquet", 'date_until_banquet_sinfo', 'meilleur_banquet',
                                   'banquet_de_l_univers', 'banquet_epl', 'meilleur_banquet_de_l_univers'],
                          pass_context=False)
        async def banquet_sinfo(self):
            """Give the number of day until BANQUET SINFO"""
            today = date.today()
            date_banquet = date(2019, 4, 23)
            delta = date_banquet - today
            if delta.days == 0:
                msg = "Trop bien c'est le jour J, j'ai vraiment hâte d'y être :D"
            elif delta.days == 1:
                msg = "Demain, se déroulera le meilleur banquet de l'univers :D"
            elif delta.days == 7:
                msg = "Dans une semaine, c'est le banquet SINFO, viendez ! :D"
            elif delta.days == 50:
                msg = "Aujourd'hui c'est le banquet elec.... mais bon, on s'en ballec :D Notre banquet (le meilleur " \
                      "de l'univers), c'est dans 50 jours :D "
                # TODO identifier tous les elecs du discord
            else:
                msg = 'J-{}'.format(delta.days)
            await self.client.say(msg)

        @commands.command(pass_context=False)
        async def jeanne(self):
            """Who is Jeanne ?"""
            await self.client.say("AU SECOUUUUUUUURS !\nhttps://tenor.com/GfhV.gif")

        @commands.command(pass_context=False)
        async def philippe(self):
            """Commande à utiliser avec *beaucoup* de précautions"""
            choices = ["SALAUD !", "JE SAIS OÙ TU TE CACHES !", "VIENS ICI QUE JE TE BUTE SALE ENCULÉ",
                       "https://tenor.com/3Qx2.gif", "TA GUEULE !"]
            msg = random.choice(choices)
            await self.client.say(msg)

        @commands.command(aliases=['shrug'], pass_context=True)
        async def goodenough(self, context):
            """Shrug David Goodenough style"""
            await self.client.send_file(self, context.message.channel, goodname)

        @commands.command(pass_context=True)
        async def bogaert(self, context):
            """Face of heaven"""
            await self.client.send_file(self, context.message.channel, bogname)

        @commands.command(aliases=['https://tenor.com/NMDa.gif'], pass_context=False)
        async def hello_there(self):
            """Hello there (tip: try with a gif url command)"""
            await self.client.say("https://tenor.com/V1tn.gif ")

    class Utilitary:
        def __init__(self, bot):
            self.client = bot

        """
            This command is greatly inspired by the bot of DXsmiley on github:
            https://github.com/DXsmiley/LatexBot
            To implement this command you must install on linux:
            texlive, dvipng
        """
        @commands.command(aliases=['tex'], pass_context=True)
        async def latex(self, context):
            """Answer with the text send, generated in latex. (in the align* environment)"""
            m = context.message

            my_latex = m.content[m.content.find(" "):].strip()
            num = str(random.randint(0, 2 ** 31))
            fn = generate_image(my_latex, num)

            if fn and os.path.getsize(fn) > 0:
                await self.client.send_file(m.channel, fn)
            else:
                await self.client.say('Something broke. Check the syntax of your message. :frowning:')

            cleanup_output_files(num)

    client.add_cog(Moderate(client))
    client.add_cog(Courses(client))
    client.add_cog(Random(client))
    client.add_cog(Utilitary(client))
