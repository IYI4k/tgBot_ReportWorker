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

import app.keyboards as keyboards

router = Router()

dbWorker = DBWorker(DB_host, DB_port, DB_database, DB_user, DB_password)
table_Users = Table("public.\"Users\"", ["id", "telegram_id", "first_name", "last_name", "reports"])
table_Reports = Table("public.\"Reports\"", ["id", "telegram_id", "report_text", "is_approved"])
table_UserReportGroups = Table("public.\"UserReportGroups\"", ["id", "telegram_id", "report_groups"])
reportSender = ReportSender(dbWorker, table_UserReportGroups)

class MyStates(StatesGroup):
    waiting_for_report = State()

@router.message(CommandStart())
async def commandStart(message: Message, state: FSMContext):
    reportGroups = dbWorker.SelectOneBy(table_UserReportGroups, table_UserReportGroups.rows_no_id, "telegram_id", str(message.from_user.id))

    if (reportGroups == None):
        dbWorker.Insert(table_ReportGroup, {"telegram_id": message.from_user.id, "report_groups": "common_recipient"})
        reportGroups = (message.from_user.id, "common_recipient")

    await message.answer(f"Здравствуйте, {message.from_user.first_name} {message.from_user.last_name}!\nНажмите '/send', чтобы начать отправку отчёта\nНажмите '/start', чтобы перезапустить бота", reply_markup=keyboards.main)

@router.message(Command("send"))
async def somedef(message: Message, state: FSMContext):
    #user = User(message.from_user.id, message.from_user.first_name, message.from_user.last_name, True)
    #dbWorker.InsertOnConflict(table_Users, user.ToDict(), "telegram_id")
    await message.answer("Введите отчёт")
    await state.set_state(MyStates.waiting_for_report)     


@router.message(MyStates.waiting_for_report)
async def get_text(message: Message, state: FSMContext):
    try:
        dbWorker.Insert(table_Reports, {"telegram_id": message.from_user.id, "report": message.text, "is_approved": None})
        report = dbWorker.SelectLastByReportBy(table_Reports, table_Reports.rows, "telegram_id", str(message.from_user.id), "id")
        dbWorker.Insert(table_Users, {"telegram_id": message.from_user.id, "first_name": message.from_user.first_name, "last_name": message.from_user.last_name, "reports": report[0]})

        recipients = reportSender.GetRecipients(message.from_user.id)
        
        for recipient in recipients:
            await message.bot.send_message(recipient, f"Отчёт от: {message.from_user.first_name} {message.from_user.last_name}\n{message.text}")

        await message.answer("Отчёт отправлен!")

        if (recipients == set()):
            await message.bot.send_message(message.from_user.id, "Но никто не указан как получатель отчёта, поэтому отчёт просто сохранился в базе данных")

        await state.clear()
    except:
        await message.answer("Произошла ошибка при отправке отчёта")