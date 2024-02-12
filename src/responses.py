from src import personas
from src.log import logger
from asgiref.sync import sync_to_async
from EdgeGPT.EdgeGPT import ConversationStyle


async def official_handle_response(message, client, persona) -> str:
    return await sync_to_async(client.chatbots[persona].ask)(message)

# prompt engineering
async def switch_persona(persona, client) -> None:
    #print("Prompt when switching persona:", personas.PERSONAS, persona)
    client.chatbots[persona] = client.get_chatbot_model(prompt=personas.PERSONAS.get(persona))