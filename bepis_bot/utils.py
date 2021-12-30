import pkgutil
from collections import defaultdict

from . import errors
from . import constants


def iter_module_specs(path, names=None, prefix=''):
  real_prefix = prefix
  prefix = f'{constants.plugin_prefix}.{prefix}'
  path = str(path)
  importer = pkgutil.get_importer(path)

  if names:
    for name in names:
      spec = importer.find_spec(prefix + name)
      if not spec:
        raise errors.PluginNotFoundError(f'{name} was not found at the path {path}')
      yield (real_prefix + name, spec)
    return

  for info in pkgutil.iter_modules([path], prefix=prefix):
    yield (
      info.name.removeprefix(f'{constants.plugin_prefix}.'),
      info.module_finder.find_spec(info.name)
    )


class keydefaultdict(defaultdict):
  def __missing__(self, key):
    if self.default_factory is None:
      raise KeyError(key)
    ret = self[key] = self.default_factory(key)
    return ret

