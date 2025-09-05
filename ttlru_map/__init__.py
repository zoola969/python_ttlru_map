from importlib.metadata import version

from ._exceptions import TTLMapError, TTLMapInvalidConfigError
from ._ttl_map import TTLMap

__version__ = version("ttlru_map")

__all__ = [
    "TTLMap",
    "TTLMapError",
    "TTLMapInvalidConfigError",
]
