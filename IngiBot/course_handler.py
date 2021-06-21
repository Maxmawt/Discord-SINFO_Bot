# created by Sami Bosch on Thursday, 08 November 2018

import discord


async def create_course(name, guild):
    """Takes a name, bot and server and creates a role and channel of that name on the server. The role has permission
    to read on the channel."""
    role = await guild.create_role(name=name.upper())

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await guild.create_text_channel(name, overwrites=overwrites)

    return channel, role


def get_courses(server):
    annonceur = discord.utils.get(server.roles, name="Annonceur")
    courses = []

    for course in server.roles:
        if course < annonceur and course != server.default_role:
            courses.append(course.name)

    return sorted(courses)
