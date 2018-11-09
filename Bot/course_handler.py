# created by Sami Bosch on Thursday, 08 November 2018

import discord


async def create_course(name, client, server):
    """Takes a name, bot and server and creates a role and channel of that name on the server. The role has permission
    to read on the channel."""
    role = await client.create_role(server, name=name.upper())

    block_perms = discord.PermissionOverwrite(read_messages=False)
    read_perms = discord.PermissionOverwrite(read_messages=True)

    channel = await client.create_channel(server, name, (server.default_role, block_perms), (role, read_perms))

    return channel, role


def get_courses(server):
    annonceur = discord.utils.get(server.roles, name="Annonceur")
    courses = []

    for course in server.roles:
        if course < annonceur and course != server.default_role:
            courses.append(course.name)

    return sorted(courses)
