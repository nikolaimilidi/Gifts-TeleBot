import asyncio

import aiohttp
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

logging.basicConfig(level=logging.INFO)

bot = Bot(token='8377828328:AAE5OIlE_577ysb5-ha0DNjdSTyk4J3GvhU')
dp = Dispatcher()
router = Router()
dp.include_router(router)

class PurchasingGift(StatesGroup):
    choosing_gift = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id  # Получается айди пользователя
    user_full_name = message.from_user.full_name  # Получается ФИО пользователя
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://127.0.0.1:8000/api/user/{user_id}/') as response:

            if response.status == 404:
                await session.post(
                    'http://127.0.0.1:8000/api/user/',
                    json={
                        'telegram_id': user_id,
                        'full_name': user_full_name
                    }
                )

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Telegram Gifts", callback_data='gifts'))
    keyboard.row(InlineKeyboardButton(text="Мои подарки", callback_data='my_gifts'))

    await message.answer(
        "Добро пожаловать в Telegram NFT Gifts. \nНаш бот для поиска подарков:",
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(lambda c: c.data == "my_gifts")
async def my_gifts_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

@router.callback_query(lambda c: c.data == "gifts")
async def gifts_callback(callback_query: types.CallbackQuery):

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Поиск подарков", callback_data="search"))
    keyboard.row(InlineKeyboardButton(text="Купить запрос", callback_data="buy_request"))
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))

    await callback_query.message.edit_text(
        "Какой-то текст, хз",
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(lambda c: c.data == "search")
async def search_callback(callback_query: types.CallbackQuery):

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Сохраненный запрос", callback_data="saved_request1"))
    keyboard.row(InlineKeyboardButton(text="Сохраненный запрос", callback_data="saved_request2"))
    keyboard.row(InlineKeyboardButton(text="Сохраненный запрос", callback_data="saved_request3"))
    keyboard.row(InlineKeyboardButton(text="Пагинация", callback_data="pagination"))
    keyboard.row(InlineKeyboardButton(text="Новый запрос", callback_data="new_request"))
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))

    await callback_query.message.edit_text(
        "Ниже вы увидите свои сохраненные запросы",
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(StateFilter(None), lambda c: c.data == "new_request")
async def new_request_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://127.0.0.1:8000/api/gift') as response:
            gifts = await response.json()

            keyboard = InlineKeyboardBuilder()
            for gift in gifts:
                keyboard.row(InlineKeyboardButton(text=gift['name'], callback_data=f"gift_{gift['id']}"))

            await callback_query.message.answer(
                "Выберите имя подарка",
                reply_markup=keyboard.as_markup()
            )
            await state.set_state(PurchasingGift.choosing_gift)

@router.callback_query(lambda c: c.data.startswith("gift_"))
async def gift_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(choosen_gift=callback_query.data.split("_")[1])
    data = callback_query.data  # gift_1 (здесь будет рандомна цифра)
    splitted_data = data.split('_')  # list -> ["gift", "1"]
    gift_id = splitted_data[1]  # Айдишник подарка - 1
    await callback_query.answer(gift_id)
    async with aiohttp.ClientSession() as session:
        response = await session.get(f'http://127.0.0.1:8000/api/gift/{gift_id}/')
        gift = await response.json()  # {'id': 1, 'name': 'Cigar', 'model': 'Hui', 'number': 123}

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{gift_id}"))
    keyboard.add(InlineKeyboardButton(text="Отменить", callback_data="cancel_choice"))

    await callback_query.message.answer(
        "Подтвердите покупку подарка:\n\n"
        f"Название подарка: {gift['name']}\n"
        f"Модель подарка: {gift['model']}\n"
        f"Номер подарка: {gift['number']}\n",
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_callback(callback_query: types.CallbackQuery, state: FSMContext):
    gift_id = await state.get_data()
    user_id = callback_query.from_user.id

    async with aiohttp.ClientSession() as session:
        await session.post(
            'http://127.0.0.1:8000/api/purchases/',
            json={
                "user": user_id,
                "gift": gift_id['choosen_gift'],
            }
        )

    await callback_query.message.edit_text(
        f"Поздравляем с покупкой подарка!"
    )
    await state.clear()

@router.callback_query(lambda c: c.data == "cancel_choice")
async def cancel_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Sosi huy")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
