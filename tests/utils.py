from unittest.mock import Mock

LockMock = lambda: Mock(__enter__=Mock(), __exit__=Mock())  # noqa: E731
