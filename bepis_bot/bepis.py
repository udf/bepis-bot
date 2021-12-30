import importlib
import logging
import sys

from telethon import TelegramClient

from .classes import PluginModule
from .utils import keydefaultdict, iter_module_specs
from .constants import plugin_prefix


class BepisClient(TelegramClient):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.logger = logging.getLogger('bepis')
    self._plugins = keydefaultdict(PluginModule)
    self.me = None

  def make_plugin_getter(self, namespace):
    def wrapped(name):
      return self._plugins[f'{namespace}{name}']
    return wrapped

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
    for (name, spec) in iter_module_specs(path, plugin_names, prefix=namespace):
      if self._plugins[name]._module:
        conflict = self._plugins[name]._module
        raise ValueError(
          f'Plugin name collision when importing {spec.origin} as {name}! '
          f'Plugin already loaded from {conflict.__file__}'
          '\nConsider passing/changing the namespace to load_plugins().'
        )
      specs[name] = spec

    modules = []
    for name, spec in specs.items():
      module = importlib.util.module_from_spec(spec)
      self.logger.info(f'Loading plugin {name} from {module.__file__}')
      runtime.client = self
      runtime.logger = logging.getLogger(name)
      runtime.require = self.make_plugin_getter(namespace)
      # allow relative imports inside plugin modules
      sys.modules[spec.name] = module
      try:
        spec.loader.exec_module(module)
      except:
        self.logger.exception(f'Unexpected exception loading plugin')
        raise
      finally:
        del sys.modules[spec.name]
      self._plugins[name]._module = module
      modules.append(module)

    for module in modules:
      on_load = getattr(module, 'on_load', None)
      if on_load:
        try:
          await on_load()
        except:
          self.logger.exception(f'Unexpected exception initializing plugin')
          raise


# Insert runtime module so plugins can import it by name
from . import runtime
sys.modules['bepis_bot.runtime'] = runtime