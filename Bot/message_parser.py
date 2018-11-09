# created by Sami Bosch on Thursday, 08 November 2018

# This file contains all functions necessary to reply to messages

import discord

from course_handler import create_course, get_courses
from discord_utils import AsyncTimer

commands = ['yo bot', 'yea bot', 'yea boi']


def init(client):
    @client.command(pass_context=True)
    async def ban(context):
        """Takes a list of mentioned users + optionally an int. Bans all users in list, and if int has been supplied,
        unbans them after given time in days."""
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
                await client.ban(member, delete_message_days=0)
                await client.say("banned {} for {} days (-1 = indefinite)".format(member.nick, unban_time))

            if unban_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await client.unban(m.server, member)
                        await client.send_message(m.channel, "unbanned {}".format(member.nick))
                AsyncTimer(unban_time * 86400, unban_all)
        else:
            await client.say("You do not have the permission to ban users")

    @client.command(pass_context=True)
    async def kick(context):
        """Takes a list of mentioned users and kicks them all."""
        m = context.message
        if m.author.server_permissions.kick_members:
            for member in m.mentions:
                await client.kick(member)
                await client.say("kicked {}".format(member.nick))
        else:
            await client.say("You do not have the permission to kick users")

    @client.command(aliases=['mute', 'silence'], pass_context=True)
    async def timeout(context):
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
                await client.add_roles(member, muted)
                await client.say("Muted {} for {} minutes".format(member.nick, int(mute_time)))
            if mute_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await client.remove_roles(member, muted)
                        await client.send_message(m.channel, "Unmuted {}".format(member.nick))

                AsyncTimer(mute_time * 60, unban_all)
        elif mute_time == -1:
            await client.say("Please provide a time (in minutes)")
        else:
            await client.say("You do not have the permission to ban users")

    @client.command(aliases=['ac'], pass_context=True)
    async def add_course(context):
        """Creates a channel and role for a course."""
        m = context.message
        u = m.author
        if u.server_permissions.manage_channels:
            message = m.content
            if message.find(" ") > 0:
                name = message[message.find(" ") + 1:]
                role = discord.get(m.server.roles, name=name.upper())
                if role:
                    await client.say("Course exists!")
                else:
                    await create_course(name, client, m.server)
                    await client.say("Created channel and role {}".format(name))
            else:
                await client.say("Please provide a name")
        else:
            await client.say("You don't have the permissions to use this command.")

    @client.command(aliases=['follow'], pass_context=True)
    async def follow_course(context):
        m = context.message
        u = m.author

        message = m.content
        if message.find(" ") > 0:
            name = message[message.find(" ") + 1:]
            role = discord.utils.get(m.server.roles, name=name.upper())
            if role:
                annonceur = discord.utils.get(m.server.roles, name="Annonceur")
                if role >= annonceur:
                    await client.say("You cannot request that role!")
                else:
                    await client.add_roles(u, role)
                    await client.say("{} now has access to {}".format(u.nick, name))
            else:
                await client.say("Please give the name of an existing course")
        else:
            await client.say("Please provide a course to follow")

    @client.command(aliases=['unfollow'], pass_context=True)
    async def unfollow_course(context):
        m = context.message
        u = m.author

        message = m.content
        if message.find(" ") > 0:
            name = message[message.find(" ") + 1:]
            role = discord.utils.get(m.server.roles, name=name.upper())
            if role:
                annonceur = discord.utils.get(m.server.roles, name="Annonceur")
                if role >= annonceur:
                    await client.say("You cannot request that role!")
                else:
                    await client.remove_roles(u, role)
                    await client.say("{} now no longer has access to {}".format(u.nick, name))
            else:
                await client.say("Please give the name of an existing course")
        else:
            await client.say("Please provide a course to follow")

    @client.command(aliases=['list'], pass_context=True)
    async def list_courses(context):
        courses = get_courses(context.message.server)

        s = "| "
        for course in courses:
            s += course + " | "
        await client.say(s.strip())
