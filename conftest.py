from __future__ import annotations

import os
from collections.abc import Iterator

import pytest


@pytest.fixture
def umask_0002() -> Iterator[None]:
    previous = os.umask(0o002)
    try:
        yield
    finally:
        os.umask(previous)
