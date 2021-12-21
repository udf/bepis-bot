import importlib
import logging
import pkgutil
import sys
import types
from collections import defaultdict

from telethon import TelegramClient

from .utils import keydefaultdict, iter_module_specs
from .errors import PluginNotLoadedError
# Insert runtime module so plugins can import it by name
from . import runtime
sys.modules['bepis_bot.runtime'] = runtime


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

  async def load_plugins(self, path, plugin_names=None, namespace=''):
    """
    Loads plugins from a path

    :param str path: Path to load plugins from
    :param list plugin_names:
      Plugins to load from path, if unspecified all plugins will be loaded
    :param str namespace:
      Namespace to prefix the internal name of the plugin, useful if you have
      multiple plugins with the same name, defaults to empty
    """

    namespace = f'{namespace}.' if namespace else ''
    specs = {}
    for spec in iter_module_specs(path, plugin_names, prefix=namespace):
      if self._plugins[spec.name]._module:
        conflict = self._plugins[spec.name]._module
        raise ValueError(
          f'Plugin name collision when importing {spec.origin} as {spec.name}! '
          f'Plugin already loaded from {conflict.__file__}'
          '\nConsider passing/changing the namespace to load_plugins().'
        )
      specs[spec.name] = spec

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
