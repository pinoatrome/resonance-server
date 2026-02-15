# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

from __future__ import annotations

from typing import Any

import pytest
import re
from raopbridge.bridge import RaopBridge


@pytest.fixture
def popen_factory():
    class MockPopen:
        def __init__(self, **kwargs):
            self.kwargs=kwargs

        def kill(self) -> None:
            pass

    def _make(**kwargs):
        return MockPopen(**kwargs)
    return _make


@pytest.fixture
def raop_bridge_factory(popen_factory):
    def _make(**kwargs) -> RaopBridge:
        _started = kwargs.pop('started', False)
        b_value = kwargs.pop('bin') if 'bin' in kwargs else 'squeeze2raop'
        i_value = kwargs.pop('interface') if 'interface' in kwargs else '127.0.0.1'
        dd_value = kwargs.pop('data_dir') if 'data_dir' in kwargs else '.'
        instance = RaopBridge(
            bin=b_value,
            interface=i_value,
            data_dir=dd_value,
            **kwargs
        )
        if _started and instance.active_at_startup:
            instance.bridge_process = popen_factory()
        return instance

    return _make


@pytest.fixture
def raw_config_factory():
    def _make(**kwargs) -> str:
        from .fixtures.config import full_config
        for key in kwargs:
            value = kwargs[key]
            full_config = re.sub(f'<{key}>(.*)</{key}>', f'<{key}>{value}</{key}>', full_config)
        return full_config

    return _make


@pytest.fixture
def command_context_factory():
    def _make(**kwargs) -> Any:
        return None
    return _make

