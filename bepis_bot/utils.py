import pkgutil
from collections import defaultdict

from . import errors


def iter_module_specs(path, names=None, prefix=''):
  path = str(path)
  importer = pkgutil.get_importer(path)

  if names:
    for name in names:
      spec = importer.find_spec(prefix + name)
      if not spec:
        raise errors.PluginNotFoundError(f'{name} was not found at the path {path}')
      yield spec
    return

  for info in pkgutil.iter_modules([path], prefix=prefix):
    yield info.module_finder.find_spec(info.name)


class keydefaultdict(defaultdict):
  def __missing__(self, key):
    if self.default_factory is None:
      raise KeyError(key)
    ret = self[key] = self.default_factory(key)
    return ret

