import os
from urllib.parse import quote
import booru
import asyncio
import logging
import sys
import random
import schedule

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

dp = Dispatcher()
bot = ''


# I know that is poor, but I don't want use sql
with open(r'db\token.txt', encoding='utf-8', mode='r') as file:
    TOKEN = file.readline()

with open(r'db\users.txt', encoding='utf-8', mode='r') as file:
    users = dict()
    for a in file.read().split("\n"):
        if a != '':
            a = a.split(" ")
            users[a[0]] = f'{a[1]} {a[2]}'

with open(r'db\tags.txt', encoding='utf-8', mode='r') as file:
    tags = file.read().split("\n")

links = dict()
for tag in tags:
    with open(fr'db\tags\{tag}.txt', encoding='utf-8', mode='r') as file:
        links[tag] = list(file.read().split("\n"))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if str(message.chat.id) not in users:
        users[str(message.chat.id)] = '- -'
    await message.answer(f'Hi, {message.chat.first_name}.\n' +
                         f'This bot can send you images from anime sites.\n' +
                         f'To subscribe on a tag, simply send the <b>english</b> tag name to the bot. ' +
                         f'For example, if you want to subscribe to the tag 2b (from nier:automata)' +
                         f', just send "2b (nier:automata)" to the bot. ' +
                         f'You will receive images related to the subscribed tag.')


@dp.message(Command('/img'))
async def command_img_handler(message: types.Message, log: bool):
    if log:
        loggi(message)
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


def sendd(date : str) -> None:
    for loc_user in users:
        if loc_user.split(' ')[1] == str(date):
            command_img_handler(message=None, log=False)


@dp.message(Command('/schedule'))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='Утром (8:00 МСК)',
        callback_data="schedule_morning")
    )
    builder.add(types.InlineKeyboardButton(
        text='Вечером (20:00 МСК)',
        callback_data="schedule_evening")
    )
    await message.answer(
        "Когда отправлять картинки",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data.startswith("schedule_"))
async def callbacks_num(callback: types.CallbackQuery):
    userid = str(callback.from_user.id)
    user_value = users.get(userid)

    action = callback.data.split("_")[1]
    if action == "morning":
        users[userid] = users.get(userid).split(' ')[1] + str(0)
    elif action == "evening":
        users[userid] = users.get(userid).split(' ')[1] + str(1)
    await callback.message.edit_text(f"Вы будете получать картинки {'вечером' if user_value == 0 else 'утром'}")
    await callback.answer()


def loggi(message: Message):
    with open(fr'db\requests.txt', encoding='utf-8', mode='a') as f:
        if message.chat.last_name is not None:
            f.write(f'{message.chat.id} {message.chat.first_name} {message.chat.last_name}\n')
        else:
            f.write(f'{message.chat.id} {message.chat.first_name}\n')

@dp.message()
async def echo_handler(message: types.Message) -> None:
    loc_tag = quote(message.text.lower().replace(' ', '_'))  # normalise and set locally
    if loc_tag not in tags:
        try:
            loc_tags = booru.get_ids_by_tag(loc_tag)
        except Exception as ex:
            await message.answer(str(ex))
            return
        with open(fr'db\tags\{loc_tag}.txt', encoding='utf-8', mode='a') as f:
            f.write(loc_tags)
        tags.append(loc_tag)
        links[loc_tag] = loc_tags.split("\n")
        await message.answer(f'collected tag {message.text} now you can get images by /img')
    else:
        await message.answer(f'You subscribed to {message.text}. To unsubscribe, send another tag')
    users.update({str(message.chat.id): str(tags.index(loc_tag))})


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # schedule.every().day.at("03:00").do(send(1))
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        with open(r'db\users.txt', mode='w') as file_:
            for key in users:
                value1 = users[key.split(' ')[0]]
                value2 = users[key.split(' ')[1]]
                file_.write(f'{key} {value1} {value2}\n')
        with open(r'db\tags.txt', encoding='utf-8', mode='w') as file:
            file.write('\n'.join(tags))
