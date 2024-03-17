import os
from urllib.parse import quote
import booru
import asyncio
import logging
import sys
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

dp = Dispatcher()
bot = ''
with open(r'db\token.txt', encoding='utf-8', mode='r') as file:
    TOKEN = file.readline()

with open(r'db\users.txt', encoding='utf-8', mode='r') as file:
    users = dict()
    for a in file.read().split("\n"):
        if a != '':
            a = a.split(" ")
            users[a[0]] = a[1]

with open(r'db\tags.txt', encoding='utf-8', mode='r') as file:
    tags = file.read().split("\n")

links = dict()
for tag in tags:
    with open(fr'db\tags\{tag}.txt', encoding='utf-8', mode='r') as file:
        links[tag] = list(file.read().split("\n"))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if str(message.chat.id) in users:
        await message.answer('You have already started chat')
    else:
        users[str(message.chat.id)] = '-'
        await message.answer(f'Hi, {message.chat.first_name}.\n' +
                             f'This bot can send you image from booru sites.\n' +
                             f'Send me tag from booru site and get image by /img')


@dp.message(F.text == '/img')
async def command_img_handler(message: types.Message):
    if message.text != '/img':
        pass
    with open(fr'db\requests.txt', encoding='utf-8', mode='a') as f:
        if message.chat.last_name is not None:
            f.write(f'{message.chat.id} {message.chat.first_name} {message.chat.last_name}\n')
        else:
            f.write(f'{message.chat.id} {message.chat.first_name}\n')
    tag_by_user = users.get(str(message.chat.id))
    if tag_by_user == '-':
        await message.answer('before ask an image, add your tag')
    # for easier debug
    tag_by_id = tags[int(tag_by_user)]
    links_list = links.get(tag_by_id)
    len_of_list_of_tags = len(links_list) - 1
    random_index = random.randint(0, len_of_list_of_tags)
    link = str(links.get(tag_by_id)[random_index])
    await bot.send_photo(message.chat.id,
                         photo=booru.get_image_link_by_id(link))


@dp.message()
async def echo_handler(message: types.Message) -> None:
    loc_tag = message.text.lower()
    if loc_tag not in tags:
        try:
            loc_tags = booru.get_ids_by_tag(quote(loc_tag))
        except Exception as ex:
            await message.answer(str(ex))
            return
        tags.append(loc_tag)
        users.update({str(message.chat.id): str(len(tags) - 1)})
        with open(fr'db\tags\{loc_tag}.txt', encoding='utf-8', mode='a') as f:
            f.write(loc_tags)
        tags.append(loc_tag)
        links[loc_tag] = loc_tags.split("\n")
    await message.answer(f'collected tag {loc_tag}')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        os.remove(r'db\users.txt')
        with open(r'db\users.txt', mode='a') as file_:
            for key in users:
                file_.write(f'{key} {users[key]}\n')
        with open(r'db\tags.txt', encoding='utf-8', mode='w') as file:
            file.write('\n'.join(tags))
