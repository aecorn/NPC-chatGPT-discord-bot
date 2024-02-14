import discord
from worldanvil.npcs import PERSONAS, LOCATIONS


async def setup_npc_channels(client, location="Prinberg"):
    for guild in client.guilds:
        if guild.name == "Zarthuga":
            break
    else:
        raise ValueError("Wrong server?")
    for category in guild.categories:
        if category.name == "NPCs":
            break
    else:
        await guild.create_category("NPCs")
    existing_channels = [cha.name for cha in category.channels]
    
    added, deleted = [], []
    
    filtered_personas = {k: v for k, v in PERSONAS.items() if k.lower().endswith(location.lower())}

    for channel in existing_channels:
        if channel not in filtered_personas:
            deleted += [channel]
            await [cha for cha in category.channels if cha.name == channel][0].delete()
    for character in filtered_personas:
        if character not in existing_channels:
            added += [character]
            new_channel = await category.create_text_channel(character)
            npc_description = filtered_personas[character]["full_name"] + ":\n" + filtered_personas[character]["description"]
            with open(filtered_personas[character]["img"], 'rb') as f:
                picture = discord.File(f)
                await new_channel.send(file=picture)
            await new_channel.send(npc_description + "\nUse the command /talk to talk to NPCs.")

    # Create travel-log channel if not exists
    for maincategory in guild.categories:
        if maincategory.name == "Text Channels":
            break
    possib_travel = [cha for cha in maincategory.channels if cha.name == "travel-log"]
    if not possib_travel:
        travel_log = await maincategory.create_text_channel("travel-log")
    else:
        travel_log = possib_travel[0]

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