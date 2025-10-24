import sys
from os import getenv

from aiogram import html, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.classes import *
from config import DB_host
from config import DB_port
from config import DB_database
from config import DB_user
from config import DB_password

router = Router()

dbWorker = DBWorker(DB_host, DB_port, DB_database, DB_user, DB_password)
table_Users = Table("public.\"Users\"", ["id", "telegram_id", "first_name", "last_name", "orders"])
table_Orders = Table("public.\"Orders\"", ["id", "telegram_id", "order_text", "is_approved"])

class MyStates(StatesGroup):
    waiting_for_order = State()

@router.message(Command("send"))
async def somedef(message: Message, state: FSMContext):
    #user = User(message.from_user.id, message.from_user.first_name, message.from_user.last_name, True)
    #dbWorker.InsertOnConflict(table_Users, user.ToDict(), "telegram_id")
    await message.answer("Введите отчёт")
    await state.set_state(MyStates.waiting_for_order)

@router.message(MyStates.waiting_for_order)
async def get_text(message: Message, state: FSMContext):
    try:
        dbWorker.Insert(table_Orders, {"telegram_id": message.from_user.id, "order": message.text, "is_approved": None})
        order = dbWorker.SelectLastByOrderBy(table_Orders, table_Orders.rows, "telegram_id", str(message.from_user.id), "id")
        dbWorker.Insert(table_Users, {"telegram_id": message.from_user.id, "first_name": message.from_user.first_name, "last_name": message.from_user.last_name, "orders": order[0]})
        await message.answer("Отчёт отправлен!")
        await state.clear()
    except:
        await message.answer("Произошла ошибка при отправке отчёта")