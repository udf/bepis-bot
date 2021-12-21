from collections import defaultdict
import importlib
import logging
import pkgutil
import sys
import types

from telethon import TelegramClient
import telethon

# Insert runtime module so plugins can import it by name
from . import runtime
sys.modules['bepis_bot.runtime'] = runtime


class keydefaultdict(defaultdict):
  def __missing__(self, key):
    if self.default_factory is None:
      raise KeyError(key)
    ret = self[key] = self.default_factory(key)
    return ret


class PluginNotLoadedError(Exception):
  pass


class PluginModule:
  def __init__(self, name: str):
    self._name = name
    self._module: types.ModuleType = None

  def __getattr__(self, name):
    if not self._module:
      raise PluginNotLoadedError(f'Plugin "{self._name}" is not loaded')
    return getattr(self._module, name)


class BepisClient(TelegramClient):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.logger = logging.getLogger('bepis')
    self._plugins = keydefaultdict(PluginModule)
    self.me = None

  async def load_plugins_from_dir(self, path, namespace=None):
    namespace = f'{namespace}.' if namespace else ''
    specs = {}

    for info in pkgutil.iter_modules([str(path)]):
      short_name = f'{namespace}{info.name}'
      name = f'bepis._plugins.{short_name}'
      spec = info.module_finder.find_spec(info.name)

      if self._plugins[short_name]._module:
        conflict = self._plugins[short_name]._module
        raise ValueError(
          f'Plugin name collision when importing {spec.origin} as {short_name}! '
          f'Plugin already loaded from {conflict.__file__}'
          '\nConsider passing/changing the namespace to load_plugins().'
        )
      specs[short_name] = spec

    for name, spec in specs.items():
      module = importlib.util.module_from_spec(spec)
      self.logger.info(f'Loading plugin {name} from {module.__file__}')
      runtime.client = self
      runtime.logger = logging.getLogger(name)
      try:
        spec.loader.exec_module(module)
      except:
        self.logger.exception(f'Unexpected exception loading plugin')
      self._plugins[name]._module = module

  async def load_plugins(self, paths, namespace=None):
    "Loads all plugins from the specified path(s)"
    if not telethon.utils.is_list_like(paths):
      paths = [paths]

    for path in paths:
      await self.load_plugins_from_dir(path, namespace)