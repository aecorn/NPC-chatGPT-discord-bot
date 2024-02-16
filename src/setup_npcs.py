import discord
from npc_content.npcs import PERSONAS, LOCATIONS
import os

async def setup_npc_channels(client, location="Prinberg"):
    
    added, deleted = [], []
    

    personas_at_location = {k: v for k, v in PERSONAS.items() if k.lower().endswith(location.lower())}


    await keep_webhooks_for_npcs(client, personas_at_location)
    await create_missing_chatbots(client, personas_at_location)
    await remove_unused_chatbots(client, personas_at_location)
    deleted = await delete_unused_channels(client, personas_at_location)
    added = await add_new_npc_channels_and_webhooks(client, personas_at_location)
    travel_log = await get_travel_log_channel(client)
    

    msg_start = "[Current location:"
    msg_str = f"{msg_start} {location}]\n"
    #Delete the previous restart message
    async for msg in travel_log.history(limit=20):
        if msg.content.startswith(msg_str):
            #print(msg)
            await msg.delete()
    
    if added:
        npc_string = "\n".join(added)
        msg_str += f"adding these NPCs:\n{npc_string}\n"
    if deleted:
        npc_string = "\n".join(deleted)
        msg_str += f"\ndeleting these NPCs (the history in the channels are gone):\n{npc_string}\n"

    locations_img = {k.lower(): v.get("img", None) for k, v in LOCATIONS.items() if isinstance(v, dict) and "img" in v}
    with open(locations_img[location.lower()], 'rb') as f:
        loc_picture = discord.File(f)
    locations_descriptions = {k.lower(): v.get("description", None) for k, v in LOCATIONS.items() if isinstance(v, dict) and "img" in v}
    await travel_log.send(msg_str + locations_descriptions[location.lower()], file=loc_picture)


def get_guild(client):
    for guild in client.guilds:
        if guild.name == "Zarthuga":
            break
    else:
        raise ValueError("Wrong server?")
    return guild

async def get_npc_category(client):
    guild = get_guild(client)
    for category in guild.categories:
        if category.name == "NPCs":
            break
    else:
        category = await guild.create_category("NPCs")
    return category

async def get_npc_channels(client):
    npc_category = await get_npc_category(client)
    return npc_category.channels

async def get_travel_log_channel(client):
    for maincategory in get_guild(client).categories:
        if maincategory.name == "Text Channels":
            break
    possib_travel = [cha for cha in maincategory.channels if cha.name == "travel-log"]
    if not possib_travel:
        travel_log = await maincategory.create_text_channel("travel-log")
    else:
        travel_log = possib_travel[0]
    return travel_log


async def keep_webhooks_for_npcs(client, personas):
    channels = await get_npc_channels(client)
    #print(list(personas.keys()))
    #print([cha.name for cha in channels])
    #print([cha.name for cha in channels if cha.name ])
    for del_cha in [channel for channel in channels if channel.name not in list(personas.keys())]:
        #print("found channel to delete webhooks from", del_cha.name)
        hooks = await del_cha.webhooks()
        for hook in hooks:
            await hook.delete()
    for keep_cha in [channel for channel in channels if channel.name in list(personas.keys())]:
        #print("found channel to keep", keep_cha.name)
        keep_channel_webhooks = await keep_cha.webhooks()
        #print(keep_channel_webhooks)
        if keep_channel_webhooks:
            #print("Found exisitng webhook on existing channel, that we want to keep", keep_cha.name)
            client.webhooks[keep_cha.name] = keep_channel_webhooks[0]
        else:
            await create_webhook_with_avatar(client, personas, keep_cha)

async def create_webhook_with_avatar(client, personas, channel):
    #print("Creating webhook on existing channel, that we want to keep", channel.name)
    split_path = personas[channel.name]["img"].split("/")
    split_path.insert(-1, "thumbnails")
    split_path[-1] = split_path[-1].split(".")[0] + ".jpg"
    thumb_path = "/".join(split_path)
    with open(thumb_path, 'rb') as f:
        buf = f.read()
    client.webhooks[channel.name] = await channel.create_webhook(
        name=personas[channel.name]["full_name"],
        avatar=buf) 

async def create_missing_chatbots(client, personas_at_location):
    chatbots_not_on_client = {name: attrs for name, attrs in personas_at_location.items() if name not in client.chatbots}
    #print("create chatbots for:", chatbots_not_on_client)
    for persona, attrs in chatbots_not_on_client.items():
        client.chatbots[persona] = client.get_chatbot_model(prompt=attrs["prompt"])
        # See if chatbot can be restored from file
        folder = "./npc_content/saved_chatbots/"
        os.makedirs(folder, exist_ok=True)
        chatbot_path = "{folder}{persona}.json"
        if os.path.isfile(chatbot_path):
            print("Opening stored chatbot", persona)
            client.chatbots[persona].load(chatbot_path)
    
async def remove_unused_chatbots(client, personas_at_location):
    chatbots_on_client_not_at_location = {botname: chatbot for botname, chatbot in client.chatbots.items() 
                                          if botname not in personas_at_location}
    #print("remove unused chatbots for:", chatbots_on_client_not_at_location)
    # Store chatbot before deletion
    folder = "./npc_content/saved_chatbots/"
    os.makedirs(folder, exist_ok=True)
    for botname, chatbot in chatbots_on_client_not_at_location.items():
        chatbot.save(f"{folder}{botname}.json")
        del client.chatbots[botname]

async def delete_unused_channels(client, personas):
    deleted = []
    npc_channels = await get_npc_channels(client)
    for channel in npc_channels:
        if channel.name not in personas:
            deleted += [channel.name]
            await channel.delete()
    return deleted

async def add_new_npc_channels_and_webhooks(client, personas):
    added = []
    npc_channels = await get_npc_channels(client)
    npc_category = await get_npc_category(client)
    for character in personas:
        # Make new channel and webhook if character doesnt exist already
        if character not in [cha.name for cha in npc_channels]:
            added += [character]
            new_channel = await npc_category.create_text_channel(character)
            #print("Want to add webhook to new_channel")
            await create_webhook_with_avatar(client, personas, new_channel)
            npc_description = personas[character]["full_name"] + ":\n" + personas[character]["description"]
            with open(personas[character]["img"], 'rb') as f:
                picture = discord.File(f)
                await new_channel.send(file=picture)
            await new_channel.send(npc_description)
    return added