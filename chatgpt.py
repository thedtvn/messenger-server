import dataclasses
import uuid
import aiohttp
import base64
import random
from aiohttp.client_exceptions import ClientResponseError

headers_real = {"User-Agent": "Mozilla/5.0 (compatible; FantasyBot/0.1; +https://fantasybot.tech/support)"}


@dataclasses.dataclass
class Image:
    filename: str
    content: bytes


class ChatGPT:
    SSL_Mode = None

    def __init__(self):
        self.tokenlist = ["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",
                          "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",
                          "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",
                          "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",
                          "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",
                          "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",
                          "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",
                          "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"]

    async def authenticate(self):
        return "Bearer " + random.choice(self.tokenlist)  # nosec

    async def create_new_chat(self, data):
        messlist = [{"role": "system", "content": "Your name is FantasyBot and made by Fantasy Team and team website at http://fantasybot.tech/ and AI output must below 4000 characters."}]
        messlist.extend(data)
        headers = headers_real.copy()
        headers["Authorization"] = await self.authenticate()
        while True:
            try:
                async with aiohttp.ClientSession(headers=headers) as s:
                    async with s.post(f"https://api.openai.com/v1/chat/completions",
                                    timeout=None,
                                    ssl=self.SSL_Mode,
                                    raise_for_status=True,
                                    json={
                                            "model": "gpt-3.5-turbo",
                                            "messages": messlist,
                                            "temperature": 0.6
                                            }
                                    ) as r:
                        return (await r.json())["choices"][0]["message"]["content"].strip()
            except ClientResponseError as e:
                if e.status != 429:
                    raise e

    async def create_dalle(self, data, token=None):
        headers = headers_real.copy()
        headers["Authorization"] = await self.authenticate() if token is None else "Bearer " + token
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.post(f"https://api.openai.com/v1/images/generations",
                              timeout=None,
                              raise_for_status=True,
                              json={
                                  "prompt": data,
                                  "response_format": "b64_json"
                              }) as r:
                base64data = (await r.json())["data"][0]["b64_json"]
                imgdata = base64.b64decode(base64data)
                filename = f'{uuid.uuid4().hex}.jpg'
                return Image(**{"filename": filename, "content": imgdata})