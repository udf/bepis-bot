from logging import Logger
import typing

from .bepis import BepisClient
from .classes import PluginModule

client: BepisClient
logger: Logger
require: typing.Callable[[str], PluginModule]