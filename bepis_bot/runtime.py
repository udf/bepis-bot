from logging import Logger
import typing
from telethon import TelegramClient

from .classes import PluginModule


client: TelegramClient
logger: Logger
require: typing.Callable[[str], PluginModule]