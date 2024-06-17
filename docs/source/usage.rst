Usage
=====

.. _installation:

Installation
------------

To use **ttlru_map**, first install it using pip:

.. code-block:: console

   (.venv) $ pip install ttlru_map

Usage example
_____________

Imagine you want a cache that stores values for 10 seconds. You can use :py:class:`ttlru_map.TTLMap` class for that:

.. code-block:: python

   from datetime import timedelta
   from time import sleep

   from ttlru_map import TTLMap

   cache = TTLMap(ttl=timedelta(seconds=10))

   cache['key'] = 'value'
   print(cache['key'])  # 'value'

   # Wait for 10 seconds
   sleep(10)
   print(cache['key'])  # KeyError


If you want to add LRU functionality to your cache, you can `maxsize` argument
:py:class:`ttlru_map.TTLMap` class:

.. code-block:: python

    from datetime import timedelta
    from time import sleep

    from ttlru_map import TTLMap

    cache = TTLMap(ttl=timedelta(seconds=10), maxsize=2)
    cache["first"] = 1
    cache["second"] = 2
    print(cache)
    # Wait for 10 seconds
    sleep(10)
    print(cache[0])  # KeyError
    print(cache[1])  # 1

    # Add 100 more items
    for i in range(100, 200):
       cache[i] = i

    print(cache[1])  # KeyError
    print(cache[100])  # 100
