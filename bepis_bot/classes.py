import types
from .errors import PluginNotLoadedError


class PluginModule:
  """Represents a plugin module which may or may not be currently loaded"""
  def __init__(self, name: str):
    self._name = name
    self._module: types.ModuleType = None

  def __getattr__(self, name):
    if not self._module:
      raise PluginNotLoadedError(f'Plugin "{self._name}" is not loaded')
    return getattr(self._module, name)
