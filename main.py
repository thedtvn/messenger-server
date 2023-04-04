import asyncio
import aiohttp
from aiohttp import web
from chatgpt import ChatGPT

page_access_token = "EAAQ21oqZBN4kBADPeNCQ6puvvdaybFjbllKlEh0uJvbAKWWgE07Su5YPYVq8u6smq6ohwUFyHf3DLYkKIcdIFVfb9ZA19EtbZBFPmHXBYGghVwKLUr46cluuwZBZC3XYHqqJ7TTBLaU8lx3TxaeWsgiy4rfVw1X4ZCL7m5DSZBfbatZCqkk80ZCnh"
v = "v15.0"
page_id = "109581428764257"

def split_string(input_string):
    max_chars = 2000
    output_list = []
    current_string = ""
    words = input_string.splitlines()
    for word in words:
        if len(current_string + " \n" + word) <= max_chars:
            current_string += "\n " + word
        else:
            output_list.append(current_string)
            current_string = word
    if current_string:
        output_list.append(current_string)
    return output_list

async def send_event(recipient_id, type):
    async with aiohttp.ClientSession() as session:
        url = f'https://graph.facebook.com/{v}/{page_id}/messages?access_token={page_access_token}'
        payload = {
                "recipient": {"id": recipient_id},
                "sender_action": type
            }
        async with session.post(url, json=payload, raise_for_status=True) as response:
            pass

async def send_message(recipient_id, message_text):
    if len(message_text) <= 2000:
        async with aiohttp.ClientSession() as session:
            url = f'https://graph.facebook.com/{v}/{page_id}/messages?access_token={page_access_token}'
            payload = {
                "recipient": {"id": recipient_id},
                "messaging_type": "RESPONSE",
                "message": {"text": message_text},
            }
            async with session.post(url, json=payload, raise_for_status=True) as response:
                pass
    else:
        out = split_string(message_text)
        for i in out:
            await send_message(recipient_id, i)

async def get_message(message_id):
    async with aiohttp.ClientSession() as session:
        url = f'https://graph.facebook.com/{v}/{message_id}'
        params = {
            "fields": "from,message",
            "access_token": page_access_token
        }
        async with session.get(url, params=params) as response:
            data = await response.json()
            if data["from"]["id"] == page_id:
                role = "assistant"
            else:
                role = "user"
            return {"role": role, "content": data["message"]}

async def get_conversation_messages(conversation_id):
    async with aiohttp.ClientSession() as session:
        url = f'https://graph.facebook.com/{v}/{conversation_id}'
        params = {
            "fields": "messages",
            "access_token": page_access_token
        }
        async with session.get(url, params=params) as response:
            data = await response.json()
            return data.get('messages', {}).get("data")

async def send_message_hr(uid):
    async with aiohttp.ClientSession() as session:
        url = f'https://graph.facebook.com/{v}/{page_id}/conversations?platform=messenger&user_id={uid}&access_token={page_access_token}'
        async with session.get(url) as response:
            data = await response.json()
            chatid = data["data"][0]["id"]
    out  = await get_conversation_messages(chatid)
    if out:
        out.reverse()
        out = await asyncio.gather(*[get_message(i["id"]) for i in out])
        return out

app = web.Application()
routes = web.RouteTableDef()
gpt = ChatGPT()

async def mes_proseing(message_event):
    await send_event(message_event["sender"]["id"], "MARK_SEEN")
    isdone = False