import os
import discord
import asyncio
from typing import Union

from src import responses
from src.log import logger
from utils.message_utils import send_split_message, send_response_with_images
from npc_content.npcs import setup_npcs_constants

from dotenv import load_dotenv
from discord import app_commands

from revChatGPT.V3 import Chatbot
from revChatGPT.V1 import AsyncChatbot
load_dotenv()

class aclient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.current_channel = None
        self.activity = discord.Activity(type=discord.ActivityType.listening, name="/chat | /help")
        self.isPrivate = False
        self.is_replying_all = os.getenv("REPLYING_ALL")
        self.replying_all_discord_channel_id = os.getenv("REPLYING_ALL_DISCORD_CHANNEL_ID")
        self.openAI_email = os.getenv("OPENAI_EMAIL")
        self.openAI_password = os.getenv("OPENAI_PASSWORD")
        self.openAI_API_key = os.getenv("OPENAI_API_KEY")
        self.openAI_gpt_engine = os.getenv("GPT_ENGINE")
        self.chatgpt_session_token = os.getenv("SESSION_TOKEN")
        self.chatgpt_access_token = os.getenv("ACCESS_TOKEN")
        self.chatgpt_paid = os.getenv("PUID")

        config_dir = os.path.abspath(f"{__file__}/../../")
        prompt_name = 'system_prompt.txt'
        prompt_path = os.path.join(config_dir, prompt_name)
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.starting_prompt = f.read()

        self.chat_model = os.getenv("CHAT_MODEL")
        self.chatbots, self.webhooks = {}, {}
      
        self.message_queue = asyncio.Queue()

    def get_chatbot_model(self, prompt = None) -> Union[AsyncChatbot, Chatbot]:
        if not prompt:
            prompt = self.starting_prompt
        return Chatbot(api_key=self.openAI_API_key, engine=self.openAI_gpt_engine, system_prompt=prompt)

    async def process_messages(self):
        while True:
            if self.current_channel is not None:
                while not self.message_queue.empty():
                    async with self.current_channel.typing():
                        message, user_message = await self.message_queue.get()
                        try:
                            await self.send_message(message, user_message, persona = self.current_channel.name)
                        except Exception as e:
                            logger.exception(f"Error while processing message: {e}")
                        finally:
                            self.message_queue.task_done()
            await asyncio.sleep(1)


    async def enqueue_message(self, message, user_message):
        await message.response.defer(ephemeral=self.isPrivate) if self.is_replying_all == "False" else None
        await self.message_queue.put((message, user_message))

    async def send_message(self, message, user_message, persona):
        if self.is_replying_all == "False":
            author = message.user.id
        else:
            author = message.author.id
        try:
            #await user_message.user.edit(nick=PERSONAS[persona]['full_name'])
            response = (f'> <@{str(author)}>: **{user_message}** \n\n')
            response = f"{response}{PERSONAS[persona]['full_name']}: {await responses.official_handle_response(user_message, self, persona)}"
            #await message.followup.edit(name=PERSONAS[persona]['full_name'])
            #print(message)
            await send_split_message(self, response, message)
        except Exception as e:
            logger.exception(f"Error while sending : {e}")
            if self.is_replying_all == "True":
                await message.channel.send(f"> **ERROR: Something went wrong, please try again later!** \n ```ERROR MESSAGE: {e}```")
            else:
                await message.followup.send(f"> **ERROR: Something went wrong, please try again later!** \n ```ERROR MESSAGE: {e}```")

    async def send_start_prompt(self, persona):
        discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
        try:
            PERSONAS, WORLD_INFO, LOCATIONS = setup_npcs_constants()
            for persona, attributes in PERSONAS.items():
                prompt = attributes.get("prompt", None)
                if prompt:
                    if (discord_channel_id):
                        channel = self.get_channel(int(discord_channel_id))
                        logger.info(f"Send system prompt with size {len(prompt)}")
                        response = ""
                        response = f"{response}{await responses.official_handle_response(prompt, self, persona)}"
                        await channel.send(response)
                        logger.info(f"System prompt response:{response}")
                    else:
                        logger.info("No Channel selected. Skip sending system prompt.")
                else:
                    logger.info(f"Not given starting prompt. Skiping...")
        except Exception as e:
            logger.exception(f"Error while sending system prompt: {e}")


client = aclient()
