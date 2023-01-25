import aiohttp
from fake_useragent import UserAgent
import re
from colorama import *


class Gmail:
    def __init__(self, cookie):
        self.cookie = self.convert_cookie(cookie)
        self.mail = ""
        self.session = self.create_session()

    def create_session(self):
        ua = UserAgent()
        headers = {
            "user-agent": ua.random
        }
        session = aiohttp.ClientSession(headers=headers, cookies=self.cookie)
        return session

    async def get_code(self):
        letters = await self.get_letters()
        code = self.find_code(letters)
        return code

    def find_code(self, letters):
        if letters.find('Supercell ID') == -1:
            return False
        pattern = r"\[\d+\s+\d+\]"
        for match in re.finditer(pattern, letters):
            return letters[match.start() + 1:match.end() - 1].replace(' ', '')

    async def get_letters(self):
        response = await self.session.get(f'https://mail.google.com/mail/u/0/#inbox')
        letters = await response.text()
        return letters

    async def check_cookie(self):
        try:
            response = await self.session.get(f"https://mail.google.com/mail/u/0/#inbox")
            text = await response.text()
            self.mail = text.split('["mla",[["')[1].split('"')[0]
            return text
        except Exception as ex:
            print(Fore.LIGHTRED_EX + "Invalid cookie")
            return False

    def convert_cookie(self, cookie):
        converted = {}
        text = cookie.split("\n")
        for index, row in enumerate(text):
            segments = row.split("\t")
            if len(segments) == 7:
                converted[f"{segments[5].strip()}"] = segments[6].strip()

                # converted[f"cookie{index}"] = {
                #     "name": segments[5].strip(),
                #     "domain": segments[0].strip(),
                #     "value": segments[6].strip()
                # }

                # converted[f"name{index}"] = segments[5].strip()
                # converted[f"domain{index}"] = segments[0].strip()
                # converted[f"value{index}"] = segments[6].strip()

        return converted

