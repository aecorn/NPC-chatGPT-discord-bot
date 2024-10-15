import os
import openai
import asyncio
import discord
from src.log import logger
from random import randrange
from src.aclient import client
from discord import app_commands
from discord.ext.commands import has_permissions
from src import responses, setup_npcs
from npc_content.npcs import setup_npcs_constants

LOCATION = "Prinberg"

def run_discord_bot():
    @client.event
    async def on_ready():
        PERSONAS, WORLD_INFO, LOCATIONS = setup_npcs_constants()
        for persona in PERSONAS.values():
            await client.send_start_prompt(persona.get("prompt"))
        await client.tree.sync()
        
        await client.wait_until_ready()
        await setup_npcs.setup_npc_channels(client)

        loop = asyncio.get_event_loop()
        loop.create_task(client.process_messages())
        logger.info(f'{client.user} is now running!')

    @client.event
    async def on_member_join(member):
        await member.send(setup_npcs.WORLD_INFO["Description"])


    @client.tree.command(name="travel", description="Move to different location, with other NPCs")
    @has_permissions(administrator=True)
    async def travel(interaction: discord.Interaction, *, location: str):
        global LOCATION
        await interaction.response.defer(ephemeral=False)
        username = str(interaction.user)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /travel [{location}] in ({client.current_channel})")
        LOCATION = location
        result = await setup_npcs.setup_npc_channels(client, LOCATION)
        if result is None:
            await client.enqueue_message(interaction, "Could not find this location.")

    @client.tree.command(name="delnpcs", description="Delete NPC channels")
    @has_permissions(administrator=True)
    async def delnpcs(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        username = str(interaction.user)
        message = f"{username}: used /delnpcs"
        logger.info(message)
        npc_channels = await setup_npcs.get_npc_channels(client)
        for npc_channel in npc_channels:
            await npc_channel.delete()
        npc_category = await setup_npcs.get_npc_category(client)
        await npc_category.delete()
        await interaction.followup.send(message)

    @client.tree.command(name="createnpcs", description="Create NPC channels")
    @has_permissions(administrator=True)
    async def createnpcs(interaction: discord.Interaction):
        global LOCATION
        await interaction.response.defer(ephemeral=False)
        username = str(interaction.user)
        message = f"{username} used /createnpcs for location: {LOCATION}"
        logger.info(message)
        await setup_npcs.setup_npc_channels(client, LOCATION)
        await interaction.followup.send(message)


#    @client.tree.command(name="locations", description="List available locations to travel to")
#    @has_permissions(administrator=True)
#    async def locations(interaction: discord.Interaction):
#        await interaction.response.defer(ephemeral=False)
#        username = str(interaction.user)
#        logger.info(
#            f"\x1b[31m{username}\x1b[0m : /locations in ({client.current_channel})")
#        filtered_locations = [name for name, attributes in setup_npcs.LOCATIONS.items() if isinstance(attributes, dict) and not attributes["secret"]]
#        locations_str = "Locations you can /travel to are:\n" + "\n".join(filtered_locations)
#        await interaction.followup.send(locations_str)


    #@client.tree.command(name="talk", description="Talk to an NPC")
    async def talk(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        client.current_channel = interaction.channel
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /talk [{message}] in ({client.current_channel})")

        #npc_name = str(client.current_channel)
        #webhook = await client.current_channel.create_webhook(name=npc_name)
        #await webhook.send(
        #    str(message), username=npc_name, #avatar_url=member.avatar_url
        #    )
        await client.enqueue_message(interaction, message)
        #webhooks = await client.current_channel.webhooks()
        #for webhook in webhooks:
        #        await webhook.delete()
        #history = client.current_channel.history(limit=1)
        #async for msg in history:
        #    print(msg.author.display_name, interaction.guild.me.nick)
        #    if msg.author.display_name == interaction.guild.me.nick:
        #        await msg.author.edit(name=str(client.current_channel))
                #print(msg)


    @client.tree.command(name="help", description="Show help for the bot")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("""The Zarthuga-bot enables chatGPT-generating NPCs in each of their own channels.
                                    
        :star: **ADMIN COMMANDS** \n
        - `/travel` Go somewhere else, with different NPCs.
        - `/delnpcs` Delete the NPC channels and Category.
        - `/createnpcs`Create the NPC channels and Category, from the current location.
""")

        logger.info(
            "\x1b[31mSomeone needs help!\x1b[0m")

        
    @client.event
    async def on_message(message):
        if message.author.bot:
            print("message from bot")
            return
        print("on message")
        channelname = message.channel.name
        print(channelname)
        print(client.webhooks.keys())
        print(client.webhooks.get(message.channel.name))
        if channelname in client.webhooks:
            print("Channel name is in webhooks")
            print(client.webhooks[channelname].name, client.webhooks[channelname].channel.name)
            npc_response = await responses.official_handle_response(message.content, client, channelname)
            await client.webhooks[channelname].send(npc_response)


    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
