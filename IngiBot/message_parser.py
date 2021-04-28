# created by Sami Bosch on Thursday, 08 November 2018

# This file contains all functions necessary to reply to messages
import json
import random
import time
from datetime import date
import socket
from urllib.request import urlopen
from urllib.error import URLError

import discord
from discord.ext import commands

from course_handler import create_course, get_courses
from discord_utils import AsyncTimer, conv_time
from tex_handler import *
import base64
import codecs

haddock = '../haddock.json'
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, haddock)
with open(filename) as f:
    quotes = json.load(f)["quotes"]

bogaert = 'img/bogaert.png'
bogname = os.path.join(dirname, bogaert)

goodenough = 'img/goodenough.png'
goodname = os.path.join(dirname, goodenough)

ohno = 'img/ohno.png'
ohnoname = os.path.join(dirname, ohno)

starttime = time.time()


def init(client):
    class Moderate(commands.Cog):
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

            if m.author.guild_permissions.ban_members:
                for member in m.mentions:
                    await member.ban(delete_message_days=0)
                    await context.send("banned {} for {} days (-1 = indefinite)".format(member.nick, unban_time))

                if unban_time >= 0:
                    async def unban_all():
                        for mem in m.mentions:
                            await mem.unban(mem)
                            await context.send("unbanned {}".format(mem.nick))

                    AsyncTimer(unban_time * 86400, unban_all)
            else:
                await context.send("You do not have the permission to ban users")

        @commands.command(pass_context=True)
        async def kick(self, context):
            """Takes a list of mentioned users and kicks them all."""
            m = context.message
            if m.author.guild_permissions.kick_members:
                for member in m.mentions:
                    await member.kick
                    await context.send("kicked {}".format(member.nick))
            else:
                await context.send("You do not have the permission to kick users")

        @commands.command(aliases=['mute', 'silence'], pass_context=True)
        async def timeout(self, context):
            """Takes a list of mentioned users and a timeout at the end of the message and silences all users for the
            specified time in minutes."""
            m = context.message
            muted = discord.utils.get(m.guild.roles, name='Muted')
            if m.content.find(" ") > 0:
                try:
                    mute_time = float(m.content.split(" ")[-1])
                except ValueError:
                    mute_time = -1
            else:
                mute_time = -1

            if m.author.guild_permissions.manage_roles and mute_time >= 0:
                for member in m.mentions:
                    await member.add_roles(muted)
                    await context.send("Muted {} for {} minutes".format(member.nick, int(mute_time)))
                if mute_time >= 0:
                    async def unmute_all():
                        for mem in m.mentions:
                            await mem.remove_roles(muted)
                            await context.send("Unmuted {}".format(mem.nick))

                    AsyncTimer(mute_time * 60, unmute_all)
            elif mute_time == -1:
                await context.send("Please provide a time (in minutes)")
            else:
                await context.send("You do not have the permission to ban users")

    class Courses(commands.Cog):
        @commands.command(aliases=['add', 'ac'], pass_context=True)
        async def add_course(self, context):
            """Creates a channel and role for a list of courses."""
            m = context.message
            u = m.author
            if u.guild_permissions.manage_channels:
                message = m.content
                if message.find(" ") > 0:
                    for name in message.split(" ")[1:]:
                        role = discord.utils.get(m.guild.roles, name=name.upper())
                        if role:
                            await context.send("Course exists!")
                        else:
                            await create_course(name, m.guild)
                            await context.send("Created channel and role {}".format(name))
                else:
                    await context.send("Please provide a name")
            else:
                await context.send("You don't have the permissions to use this command.")

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
                    role = discord.utils.get(m.guild.roles, name=name.upper())
                    if role:
                        annonceur = discord.utils.get(m.guild.roles, name="Annonceur")
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
                await u.add_roles(*roles)
                await u.send(full.strip())
            else:
                await context.send("Please provide a course to follow")

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
                    role = discord.utils.get(m.guild.roles, name=name.upper())
                    if role:
                        annonceur = discord.utils.get(m.guild.roles, name="Annonceur")
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
                await u.remove_roles(*roles)
                await u.send(full.strip())
            else:
                await context.send("Please provide a course to follow")

        @commands.command(aliases=['list', 'lc'], pass_context=True)
        async def list_courses(self, context):
            """Lists all available courses in the guild."""
            courses = get_courses(context.message.guild)

            s = "| "
            for course in courses:
                s += course + " | "
            await context.send(s.strip())

    class Random(commands.Cog):
        @commands.command(aliases=['hello', 'hi', "bonjour", "bjr"], pass_context=True)
        async def greetings(self, context):
            """Answer with an hello message. DO NOT PING PEOPLE WITH THIS."""
            m = context.message
            arg = m.content[m.content.find(" "):].strip()
            if len(m.mentions) == 0 and "@everyone" not in m.content and "@here" not in m.content:
                if m.content.startswith('!bonjour') or m.content.startswith('!bjr'):
                    msg = 'Bonjour {} !'.format(arg)
                    # msg = 'Bonjour {0.author.mention} !'.format(m)
                else:
                    msg = 'Hello {} !'.format(arg)
                await context.send(msg)
                await m.delete()
            else:
                muted = discord.utils.get(m.guild.roles, name='Muted')
                await m.author.add_roles(muted)
                await context.send("Muted {} for {} minutes".format(m.author.nick, 5))

                async def unmute_all():
                    await m.author.remove_roles(muted)
                    await m.channel.send("Unmuted {}".format(m.author.nick))

                AsyncTimer(5 * 60, unmute_all)

        @commands.command(aliases=['haddockquote', 'haddock', 'hq'], pass_context=True)
        async def haddock_says(self, context):
            """Give a quote from Haddock"""
            msg = random.choice(quotes)
            await context.send(msg)

        @commands.command(aliases=['banquet', "date_until_banquet", 'date_until_banquet_sinfo', 'meilleur_banquet',
                                   'banquet_de_l_univers', 'banquet_epl', 'meilleur_banquet_de_l_univers'],
                          pass_context=True)
        async def banquet_sinfo(self, context):
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
            elif delta.days < 0:
                msg = "Ca fait longtemps la salaud."
            else:
                msg = 'J-{}'.format(delta.days)
            await context.send(msg)

        @commands.command(pass_context=True)
        async def jeanne(self, context):
            """Who is Jeanne ?"""
            await context.send("AU SECOUUUUUUUURS !\nhttps://tenor.com/GfhV.gif")

        @commands.command(pass_context=True)
        async def philippe(self, context):
            """Commande à utiliser avec *beaucoup* de précautions"""
            choices = ["SALAUD !", "JE SAIS OÙ TU TE CACHES !", "VIENS ICI QUE JE TE BUTE SALE ENCULÉ",
                       "https://tenor.com/3Qx2.gif", "TA GUEULE !"]
            msg = random.choice(choices)
            await context.send(msg)

        @commands.command(aliases=['shrug'], pass_context=True)
        async def goodenough(self, context):
            """Shrug David Goodenough style"""
            await context.send(file=discord.File(goodname))

        @commands.command(pass_context=True)
        async def bogaert(self, context):
            """Face of heaven"""
            await context.send(file=discord.File(bogname))

        @commands.command(aliases=['https://tenor.com/NMDa.gif'], pass_context=True)
        async def hello_there(self, context):
            """Hello there (tip: try with a gif url command)"""
            await context.send("https://tenor.com/V1tn.gif ")

    class Utilitary(commands.Cog):
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
                await context.send(file=discord.File(fn))
            else:
                await context.send('Something broke. Check the syntax of your message. :frowning:')

            cleanup_output_files(num)

        @commands.command(pass_context=True)
        async def uptime(self, context):
            """Up time. Not down."""
            await context.send("Up time: {}".format(conv_time(time.time() - starttime)))

        @commands.command(pass_context=True)
        async def inginious(self, context):
            """Is it me or is inginious down?"""
            try:
                urlopen('https://inginious.info.ucl.ac.be/', timeout=5)
            except (URLError, socket.timeout):
                await context.send("Oh no, Inginious is ded.")
                await context.send(file=discord.File(ohnoname))
            else:
                await context.send("Inginious is up!")

        @commands.command(pass_context=True)
        async def ping(self, context):
            """Conveniance method to see if bot is running or not"""
            await context.send("pong !")

        @commands.command(aliases=["b64e"], pass_context=True)
        async def b64encode(self, context):
            """Encode the specified message into b64 encoding"""
            m = context.message
            if m.content.find(" ") > 0:
                # on prend tous les mots suivant
                words = m.content.split(" ")[1:]
                delimiter = ' '
                msg = delimiter.join(words)
                b64 = base64.b64encode(msg.encode('utf-8'))
                # le decode('utf-8') est utilisé pour éviter que Python n'affiche b'' en plus
                await context.send(b64.decode('utf-8'))

        @commands.command(aliases=["b64d"], pass_context=True)
        async def b64decode(self, context):
            """Decode the specified message from b64 encoding"""
            m = context.message
            if m.content.find(" ") > 0:
                arg = m.content.split(" ")[-1]
                msg = base64.b64decode(arg)
                # le decode('utf-8') est utilisé pour éviter que Python n'affiche b'' en plus
                await context.send(msg.decode('utf-8'))

        @commands.command(aliases=["sth"], pass_context=True)
        async def strtohex(self, context):
            """Encode a String into Hexadecimal representation"""
            m = context.message
            if m.content.find(" ") > 0:
                words = m.content.split(" ")[1:]
                delimiter = ' '
                arg = delimiter.join(words)
                msg = arg.encode('utf-8').hex()
                await context.send(msg)

        @commands.command(aliases=["hts"], pass_context=True)
        async def hextostr(self, context):
            """Decode a String from Hexadecimal representation"""
            m = context.message
            if m.content.find(" ") > 0:
                decode_hex = codecs.getdecoder("hex_codec")
                arg = m.content.split(" ")[-1]
                msg = decode_hex(arg)[0]
                await context.send(msg.decode('utf-8'))

    client.add_cog(Moderate())
    client.add_cog(Courses())
    client.add_cog(Random())
    client.add_cog(Utilitary())

    # All events unrelated to message parsing go here

    @client.event
    async def on_member_join(member):
        server = member.server
        welcome = server.get_channel(509372274143657984)
        await welcome.send_message("Bonjour %s et bienvenue dans le serveur SINFO! Indique ton nom et ta section "
                                   "d'études (p.ex. 'Ingi Bot - sinf') ici pour qu'un modérateur puisse te vérifier "
                                   "et te donner accès au reste du serveur.\n\nHey there and welcome %s! Please give "
                                   "your name and the studies you're following (e.g. 'Ingi Bot - sinf') so a "
                                   "moderator can verify you and give you access to the rest of the server."
                                   % (member.mention, member.mention))
