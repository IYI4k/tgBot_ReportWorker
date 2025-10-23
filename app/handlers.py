import sys
from os import getenv

from aiogram import html, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from app.classes import *

router = Router()