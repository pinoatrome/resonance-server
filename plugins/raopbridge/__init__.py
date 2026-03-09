# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.
"""
A porting to python of the Squeeze2Raop – AirPlay bridge
from https://github.com/philippe44/lms-raop

It uses a pre-compiled binary (a.k.a. the 'bridge') valid for the local O.S.
and launches it using the subprocess module

The plugin has its own preferences and reads the bridge configuration (stored in a xml file).
"""

from __future__ import annotations

import os
import asyncio
import logging

from typing import TYPE_CHECKING, Any
from pathlib import Path

from fastapi import APIRouter, Request

if TYPE_CHECKING:
    from resonance.core.events import Event
    from resonance.plugin import PluginContext
    from resonance.web.handlers import CommandContext


from .bridge import (RaopBridge, SETTINGS_FILE, default_settings, save_settings, format_server_setting)
from .config import RaopDevice
from .serializers import RaopDeviceSerializer, RaopCommonOptionsSerializer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level state (set during setup, cleared during teardown)
# ---------------------------------------------------------------------------

_raop_bridge: RaopBridge | None = None  # RaopBridge instance

# ---------------------------------------------------------------------------
# Plugin lifecycle
# ---------------------------------------------------------------------------


async def setup(ctx: PluginContext) -> None:
    """Called by PluginManager during server startup.

    Register commands, menu entries, and event subscriptions here.
    """
    global _raop_bridge
    server_info = ctx.server_info | {}
    # the raop plugin requires settings stored in a file (the data_dir is managed by the context)
    data_dir = ctx.ensure_data_dir()
    path = data_dir / SETTINGS_FILE
    if not os.path.isfile(path):
        logger.info(f'creating default settings file in {path}')
        save_settings(default_settings(), path)
    server = format_server_setting(**server_info)
    _raop_bridge = RaopBridge.from_settings(path, server=server)
    logger.info(f'RaopBridge instance loaded using settings from {path}')
    await _raop_bridge.start()
    logger.info(f'RaopBridge instance started (bridge still inactive)')

    # 1) Register a JSON-RPC command
    ctx.register_command("raopbridge", raopbridge_cmd)

    # 2) Register a menu node on Jive devices

    # 3) Subscribe to events (tracked — auto-unsubscribed on teardown)
    await ctx.subscribe("server.started", _on_server_started)

    # 4) REST
    ctx.register_route(define_api_router())

    logger.info("RaopBridge plugin setup complete")


async def teardown(ctx: PluginContext) -> None:
    """Called by PluginManager during server shutdown.

    Persist state or release resources here.
    All command/menu/event registrations are cleaned up automatically
    after this function returns — no need to unregister manually.
    """
    global _raop_bridge

    if _raop_bridge:
        await _raop_bridge.close()
    _raop_bridge = None


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------


async def _on_server_started(_: Event) -> None:
    """Log when the server is fully operational."""
    logger.info("RaopBridge plugin: server is fully started — ready to activate bridge (if autostart)")
    if not _raop_bridge:
        logger.warning('_on_server_started event handler called before plugin - exiting')
        return

    if _raop_bridge.active_at_startup:
        await _raop_bridge.activate_bridge()
        logger.info(f'bridge process active: {_raop_bridge.is_active})')


# ---------------------------------------------------------------------------
# HTTP Routes (FastAPI)
# ---------------------------------------------------------------------------


def define_api_router() -> APIRouter:

    router = APIRouter(prefix='/api/raopbridge', tags=['raopbridge'])

    @router.get("/status")
    async def get_status():
        plugin_status = "enabled" if _raop_bridge else "disabled"
        bridge_status = "active" if _raop_bridge and _raop_bridge.is_active else "inactive"
        settings = _raop_bridge.settings if _raop_bridge else {}
        return {
            "plugin": plugin_status,
            "bridge": bridge_status,
            "settings": settings
        }

    @router.get("/settings")
    async def do_get_status():
        if _raop_bridge:
            return {
                "settings": _raop_bridge.settings
            }

    @router.patch("/settings")
    async def do_patch_settings(request: Request):
        if _raop_bridge:
            body = await request.json()
            settings = list(body.items())
            return _do_save_settings(settings)

    @router.get("/settings/advanced")
    async def do_get_settings_advanced():
        if _raop_bridge:
            return await _common_options()

    @router.get("/bin-options")
    async def do_bin_options():
        from .bridge import define_valid_bin
        return define_valid_bin()

    @router.post("/activate")
    async def do_activate():
        if _raop_bridge:
            return await _activate()

    @router.post("/deactivate")
    async def do_deactivate():
        if _raop_bridge:
            return await _deactivate()

    @router.get("/device")
    async def do_devices():
        if _raop_bridge:
            return await _devices()

    @router.put("/device/{udn}")
    async def update_device(udn: str, request: Request):
        if _raop_bridge:
            body = await request.json()
            assert body['udn'] == udn, 'Invalid data'
            s = RaopDeviceSerializer(data=body)
            s.is_valid()
            await _raop_bridge.save_device(s.instance)
            return s.serialize()

    @router.delete("/device/{udn}")
    async def delete_device(udn: str):
        if _raop_bridge:
            await _raop_bridge.remove_device(udn)
            return None

    return router


# ---------------------------------------------------------------------------
# JSON-RPC command dispatcher
# ---------------------------------------------------------------------------


async def raopbridge_cmd(
    ctx: CommandContext, command: list[Any]
) -> dict[str, Any]:
    """Dispatch ``raopbridge <sub-command> …`` to the appropriate handler.

    Sub-commands:
    - ``activate`` — activate the plugin launching raop executable.
    - ``config``  — generate configuration file for the raop executable: the plugin must be de-activated.
    - ``deactivate``  — deactivate the plugin stopping the raop executable.
    - ``devices``  — list of the devices detected by the plugin.
    - ``restart``  — restart the plugin using stored settings.
    - ``save``  — update and save current plugin settings.
    """
    if _raop_bridge is None:
        return {'error': 'RaopBridge plugin not initialized'}

    sub = str(command[1]).lower() if len(command) > 1 else ""

    match sub:
        case 'activate':
            return await _activate()
        case 'config':
            return await _raop_config()
        case 'deactivate':
            return await _deactivate()
        case 'devices':
            return await _devices()
        case 'restart':
            return await _restart()
        case 'save':
            return await _save_settings(command[2:])
        case _:
            return {'error': f'Unknown raopbridge sub-command: {sub}'}


# ---------------------------------------------------------------------------
# Utility methods
# ---------------------------------------------------------------------------

async def _activate() -> dict[str, Any]:
    await _raop_bridge.activate_bridge()
    await asyncio.sleep(1)  # give it a second for bootstrap
    return {
        'result':  _raop_bridge.is_active,
    }


async def _raop_config() -> dict[str, Any]:
    if _raop_bridge.is_active:
        return {
            'error': 'The bridge is active: deactivate it to generate a configuration file'
        }
    return {
        'result':  _raop_bridge.generate_config(),
    }


async def _deactivate() -> dict[str, Any]:
    _raop_bridge.deactivate_bridge()
    await asyncio.sleep(2)  # give it a couple of seconds for terminate
    return {
        'result': not _raop_bridge.is_active,
    }


async def _restart() -> dict[str, Any]:
    """ use the stored settings to restart the plugin call ``save`` before to use the current settings"""
    global _raop_bridge

    settings_path = Path(_raop_bridge.data_dir) / SETTINGS_FILE
    await _raop_bridge.close()
    _raop_bridge = RaopBridge.from_settings(settings_path)
    await _raop_bridge.start()

    return {
        'active':  _raop_bridge.is_active,
    }


async def _common_options() -> dict[str, Any]:
    common = await _raop_bridge.parse_common_options()
    return {
        'options': RaopCommonOptionsSerializer(instance=common).serialize()
    }


async def _devices() -> dict[str, Any]:
    devices = await _raop_bridge.parse_devices()
    return {
        'devices': [RaopDeviceSerializer(instance=d).serialize() for d in devices]
    }


async def _save_settings(settings: list[str]) -> dict[str, Any]:
    """ the settings argument is a list of strings in the format key=value to update the settings
    """
    return _do_save_settings([tuple(setting.split('=', 1)) for setting in settings])


def _do_save_settings(settings: list[tuple[str, ...]]) -> dict[str, Any]:
    errors = []
    valid_keys = _raop_bridge.settings.keys()
    for setting in settings:
        if setting[0] in valid_keys:
            setattr(_raop_bridge, setting[0], setting[1])
        else:
            errors.append(f'Invalid setting name: \'{setting[0]}\'')
    if errors:
        return {
            'errors': ','.join(errors)
        }
    store_path = Path(_raop_bridge.data_dir) / SETTINGS_FILE
    save_settings(_raop_bridge.settings, store_path)

    return {
        'result':  True,
    }
