import asyncio
import aiohttp
from aiohttp import web
from chatgpt import ChatGPT

page_access_token = "EAAQ21oqZBN4kBADPeNCQ6puvvdaybFjbllKlEh0uJvbAKWWgE07Su5YPYVq8u6smq6ohwUFyHf3DLYkKIcdIFVfb9ZA19EtbZBFPmHXBYGghVwKLUr46cluuwZBZC3XYHqqJ7TTBLaU8lx3TxaeWsgiy4rfVw1X4ZCL7m5DSZBfbatZCqkk80ZCnh"
v = "v15.0"
page_id = "109581428764257"



async def typing(recipient_id, type: bool):
    async with aiohttp.ClientSession() as session:
        url = f'https://graph.facebook.com/{v}/{page_id}/messages?access_token={page_access_token}'
        payload = {
                "recipient": {"id": recipient_id},
                "sender_action": "typing_on" if type is True else "typing_off"
            }
        async with session.post(url, json=payload) as response:
            data = await response.json()

async def send_message(recipient_id, message_text):
    async with aiohttp.ClientSession() as session:
        url = f'https://graph.facebook.com/{v}/{page_id}/messages?access_token={page_access_token}'
        payload = {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": message_text},
        }
        async with session.post(url, json=payload) as response:
            data = await response.json()

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
    await typing(message_event["sender"]["id"], True)
    datamess = await send_message_hr(message_event["sender"]["id"])
    gptreturn = await gpt.create_new_chat(datamess)
    await send_message(message_event["sender"]["id"], gptreturn)

@routes.view("/wehhook")
async def webhook(request: web.Request):
    if request.method == 'GET':
        verification_token = 'b6e052b2633147628a4c5df2090fa8bd'
        verify_string = request.query['hub.verify_token']
        if verify_string == verification_token:
            challenge = request.query['hub.challenge']
            return web.Response(status=200, body=challenge)
    elif request.method == 'POST':
        data = await request.json()
        for entry in data['entry']:
            for message_event in entry['messaging']:
                asyncio.create_task(mes_proseing(message_event))
        return web.Response(status=200)
    return web.Response(status=404)

app.add_routes(routes)
web.run_app(app, port=4000)