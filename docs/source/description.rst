Overview
========

The **TTLMap** is a thread-safe dictionary with time-to-live (TTL) and max-size support.
It can be used as a simple in-memory cache.


Key features
------------

* **Simple** - The **TTLMap** derives **MutableMapping** and implements the same interface as the built-in **dict** class. It can be used as a drop-in replacement for **dict**.
* **Efficient** - The **TTLMap** is designed to be efficient in terms of both time and space complexity.
* **Thread-safe** - The **TTLMap** is thread-safe. It can be used in multi-threaded applications without any additional synchronization.
* **Lazy** - The **TTLMap** is lazy. It does not spawn any additional threads or processes. Computing the time-to-live is done only when the **TTLMap** is accessed.
* **Zero dependencies** - The **TTLMap** has no dependencies other than the Python standard library.
* **LRU support** - The **TTLMap** supports LRU (least recently used) eviction policy. It can be configured to evict either the last set item or the least recently accessed item.

Restrictions
------------
The **TTLMap** is designed to be lazy and thread-safe in case when it is accessed only by one key. The trade-off is that iteration over the **TTLMap** is not thread-safe and does not guarantee that the item will be accessible after it is returned by the iterator.
