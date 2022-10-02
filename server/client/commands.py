from enum import Enum
from client.handler import *
PREFIX = '$'

class Commands(Enum):
    #info nodes have to be called <method_name>_info
    help_info = """<prefix>help: The help command returns a list of command information panels. This is one of them."""
    list_info =  """<prefix>list: The list command returns a list of connected clients and their associated handles. It is formatted \"<prefix>Handle<prefix>Handle\" for all handles."""
    nick_info = """<prefix>nick: The nick command replaces your handle with the value provided. The input format is <prefix>nick <new_handle>"""
    async def ___list(client, msg):
        #Return list of user handles
        await client.send("Users: ")
        async with client_list_lock:
            for user in client_list:
                await client.send(f"{PREFIX}{user.handle}")
            await client.send(f"\n{len(client_list)} user(s) online.\n")

    async def ___help(client, msg):
        for key in vars(Commands):
            if type(key) == str and key.endswith("_info"):
                await client.send((Commands[key].value+"\n").replace("<prefix>",PREFIX))

    async def ___invalid(client, msg):
        await client.send(f"Invalid command. Try {PREFIX}help\n")

    async def ___nick(client, msg):
        print(msg)
        print(msg == "nick")
        print(not msg.isalnum())
        print(PREFIX in msg)
        if msg == "nick" or not msg.isalnum() or PREFIX in msg:
            await Commands.___invalid(client, msg)
            return
        async with client_list_lock:
            for user in client_list:
                if user.handle == msg:
                    await client.send(f"Handle in use. \n")
                    return
        client.set_handle(msg)
        await client.send(f"Handle set to {msg}\n")

async def get_command(message):
    try:
        if message[0] != PREFIX:
            return False
    except IndexError:
        return False
    message = message.strip()[1:]
    try:
        return vars(Commands)["_Commands___"+message]
    except (NameError, KeyError) as e:
        print(e)
        return Commands._Commands___invalid
