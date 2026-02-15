# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

from __future__ import annotations

import pytest
from unittest import mock

from pathlib import Path

from raopbridge import (
    RaopBridge, default_settings
)


class TestBridge:

    def test_default_preferences(self):
        expected = 'test-static'
        with mock.patch('raopbridge.bridge.define_valid_bin', return_value=[expected, 'test']) as mocked:
            actual = default_settings()
            assert mocked.called
        assert actual['bin'] == expected

    def test_default_preferences_invalid(self):
        with mock.patch('raopbridge.bridge.define_valid_bin', return_value=[]) as mocked:
            actual = default_settings()
            assert mocked.called
        assert actual['bin'] is None

    def test_from_settings(self) -> None:
        with mock.patch('raopbridge.bridge.load_settings', return_value=default_settings()) as mocked:
            instance = RaopBridge.from_settings(Path('/tmp'))
            assert mocked.called
        assert instance.data_dir == '/'

    def test_build_bin_args(self, raop_bridge_factory) -> None:
        p = raop_bridge_factory()
        expected = f'-Z -I -p {p.pid_file} -b {p.interface} -f {p.logging_file} -x {p.config}'.split(' ')
        actual = p.build_bin_args()
        assert actual == expected

    @pytest.mark.asyncio
    async def test_start(self, raop_bridge_factory, popen_factory) -> None:
        p = raop_bridge_factory()
        with mock.patch('raopbridge.bridge.call_executable', return_value=popen_factory()) as mocked_exec:
            with mock.patch('raopbridge.bridge.check_valid_bin') as mocked_bin:
                await p.start()
                assert mocked_bin.called
            assert mocked_exec.called
        assert p.is_active

    @pytest.mark.asyncio
    async def test_start_inactive(self, raop_bridge_factory, popen_factory) -> None:
        p = raop_bridge_factory(active_at_startup=False)
        with mock.patch('raopbridge.bridge.check_valid_bin') as mocked_bin:
            await p.start()
            assert mocked_bin.called
        assert not p.is_active

    @pytest.mark.asyncio
    async def test_close(self, raop_bridge_factory) -> None:
        p = raop_bridge_factory(started=True)
        await p.close()
        assert p.is_active is False


