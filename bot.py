import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

logging.basicConfig(level=logging.INFO)

bot = Bot(token='8377828328:AAE5OIlE_577ysb5-ha0DNjdSTyk4J3GvhU')
dp = Dispatcher()
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Telegram Gifts", callback_data="gifts"))

    await message.answer(
        "Добро пожаловать в Telegram NFT Gifts. \nНаш бот для поиска подарков:",
        reply_markup=keyboard.as_markup()
    )

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

@router.callback_query(lambda c: c.data in ["byu_request", "back"])
async def process_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(callback_query.data)

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

@router.callback_query(lambda c: c.data in ["saved_request1", "saved_request2", "saved_request3",
                                        "pagination", "new_request", "back"])
async def search_process_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(callback_query.data)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
