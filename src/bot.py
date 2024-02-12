import os
import openai
import asyncio
import discord
from src.log import logger
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, personas, responses, setup_npcs
from worldanvil.npcs import PERSONAS


def run_discord_bot():
    @client.event
    async def on_ready():
        for persona in PERSONAS:
            await client.send_start_prompt(persona)
        await client.tree.sync()
        
        await client.wait_until_ready()
        await setup_npcs.setup_npc_channels(client)

        loop = asyncio.get_event_loop()
        loop.create_task(client.process_messages())
        logger.info(f'{client.user} is now running!')
        
    @client.tree.command(name="travel", description="Move to different location, with other NPCs")
    async def travel(interaction: discord.Interaction, *, location: str):
        await interaction.response.defer(ephemeral=False)
        username = str(interaction.user)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /travel [{location}] in ({client.current_channel})")
        await setup_npcs.setup_npc_channels(client, location)
        await interaction.followup.send(f"Travelled to {location}")

    @client.tree.command(name="locations", description="List available locations to travel to")
    async def locations(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        username = str(interaction.user)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /locations in ({client.current_channel})")
        locations_str = "Locations you can /travel to are:\n" + "\n".join(set([char.split("-")[-1].capitalize() for char in PERSONAS.keys()]))
        await interaction.followup.send(locations_str)


    @client.tree.command(name="talk", description="Talk to an NPC")
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
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({client.current_channel})")

        await client.enqueue_message(interaction, message)


    @client.tree.command(name="private", description="Toggle private access")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("\x1b[31mSwitch to private mode\x1b[0m")
            await interaction.followup.send(
                "> **INFO: Next, the response will be sent via private reply. If you want to switch back to public mode, use `/public`**")
        else:
            logger.info("You already on private mode!")
            await interaction.followup.send(
                "> **WARN: You already on private mode. If you want to switch to public mode, use `/public`**")


    @client.tree.command(name="public", description="Toggle public access")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **INFO: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
            logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **WARN: You already on public mode. If you want to switch to private mode, use `/private`**")
            logger.info("You already on public mode!")


    @client.tree.command(name="replyall", description="Toggle replyAll access")
    async def replyall(interaction: discord.Interaction):
        client.replying_all_discord_channel_id = str(interaction.channel_id)
        await interaction.response.defer(ephemeral=False)
        if client.is_replying_all == "True":
            client.is_replying_all = "False"
            await interaction.followup.send(
                "> **INFO: Next, the bot will response to the Slash Command. If you want to switch back to replyAll mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to normal mode\x1b[0m")
        elif client.is_replying_all == "False":
            client.is_replying_all = "True"
            await interaction.followup.send(
                "> **INFO: Next, the bot will disable Slash Command and responding to all message in this channel only. If you want to switch back to normal mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to replyAll mode\x1b[0m")

    @client.tree.command(name="help", description="Show help for the bot")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(""":star: **BASIC COMMANDS** \n
        - `/talk [message]` Chat with ChatGPT!

        - `/travel` Go somewhere else, with different NPCs.
""")

        logger.info(
            "\x1b[31mSomeone needs help!\x1b[0m")


    @client.event
    async def on_message(message):
        if client.is_replying_all == "True":
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    client.current_channel = message.channel
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({client.current_channel})")

                    await client.enqueue_message(message, user_message)
            else:
                logger.exception("replying_all_discord_channel_id not found, please use the command `/replyall` again.")

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
