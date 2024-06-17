# Python TTL Dict

[![Documentation Status](https://readthedocs.org/projects/python-ttl-dict/badge/?version=latest)](https://python-ttl-dict.readthedocs.io/en/latest/?badge=latest)
[![license](https://img.shields.io/github/license/zoola969/python_ttlru_map.svg)](https://github.com/zoola969/python_ttlru_map/blob/main/LICENSE)
![tests](https://github.com/zoola969/python_ttlru_map/actions/workflows/tests.yml/badge.svg?branch=master)
![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![Mypy](https://img.shields.io/badge/mypy-checked-blue)
### Installation

Installation is available using `pip install python_ttlru_map`.

### Core Features

* **TTL Dict**: A **thread-safe** dictionary that automatically removes keys after a certain amount of time or if max
  size is reached.
* It can be used as a simple **in-memory cache**.
* **Simple** - The **TTLMap** derives **MutableMapping** and implements the same interface as the built-in **dict**
  class. It can be used as a drop-in replacement for **dict**.
* **Efficient** - The **TTLMap** is designed to be efficient in terms of both time and space complexity.
* **Thread-safe** - The **TTLMap** is thread-safe. It can be used in multithreaded applications without any additional
  synchronization.
* **Lazy** - The **TTLMap** is lazy. It does not spawn any additional threads or processes. Computing the time-to-live
  is done only when the **TTLMap** is accessed.
* **Zero dependencies** - The **TTLMap** has no dependencies other than the Python standard library.
* **LRU support** - The **TTLMap** supports LRU (least recently used) eviction policy. It can be configured to evict
  either the last set item or the least recently accessed item.


### Usage Examples

```python
from datetime import timedelta
from time import sleep

from ttlru_map import TTLMap

cache: TTLMap[str, str] = TTLMap(ttl=timedelta(seconds=10))

cache['key'] = 'value'
print(cache['key'])  # 'value'

# Wait for 10 seconds
sleep(10)
print(cache['key'])  # KeyError
```

If you want to add LRU functionality to your cache, you can `maxsize` argument

```python
from ttlru_map import TTLMap

cache: TTLMap[str, str] = TTLMap(ttl=None, max_size=2)

cache['key1'] = 'value1'
cache['key2'] = 'value2'
cache['key3'] = 'value3'

print(cache.get('key1'))  # None
print(cache.get('key2'))  # 'value2'
print(cache.get('key3'))  # 'value3'
```
