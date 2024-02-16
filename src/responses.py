from asgiref.sync import sync_to_async


async def official_handle_response(message, client, persona) -> str:
    return await sync_to_async(client.chatbots[persona].ask)(message)