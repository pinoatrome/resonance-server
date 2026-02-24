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

import json
import os
import logging

from typing import Any
from pathlib import Path
from fastapi import APIRouter
from resonance.plugin import PluginContext
from resonance.web.handlers import CommandContext

from .bridge import (RaopBridge, SETTINGS_FILE, default_settings, save_settings)

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
    # the raop plugin requires settings stored in a file (the data_dir is managed by the context)
    data_dir = ctx.ensure_data_dir()
    path = data_dir / SETTINGS_FILE
    if not os.path.isfile(path):
        logger.info(f'creating default settings file in {path}')
        save_settings(default_settings(), path)

    _raop_bridge = RaopBridge.from_settings(path)
    logger.info(f'RaopBridge instance loaded using settings from {path}')
    await _raop_bridge.start()
    logger.info(f'RaopBridge instance started (active: {_raop_bridge.is_active})')

    # 1) Register a JSON-RPC command
    ctx.register_command("raopbridge", cmd_config)

    # 2) Register a menu node on Jive devices

    # 3) Subscribe to events (tracked — auto-unsubscribed on teardown)
    # await ctx.subscribe("server.started", _on_server_started)

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


def define_api_router() -> APIRouter:

    router = APIRouter(prefix='/api/raopbridge', tags=['raopbridge'])

    @router.get("/status")
    async def get_status():
        plugin_status = "running" if _raop_bridge else "stopped"
        bridge_status = "active" if _raop_bridge and _raop_bridge.is_active else "inactive"
        settings = _raop_bridge.settings if _raop_bridge else {}
        return {
            "plugin": plugin_status,
            "bridge": bridge_status,
            "settings": settings
        }

    @router.get("/activate")
    @router.post("/activate")
    async def do_activate():
        if _raop_bridge:
            _raop_bridge.activate_bridge()
        return {"result": "done"}

    @router.get("/deactivate")
    @router.post("/deactivate")
    async def do_deactivate():
        if _raop_bridge:
            _raop_bridge.deactivate_bridge()
        return {"result": "done"}

    return router


async def cmd_config(
    ctx: CommandContext, command: list[Any]
) -> dict[str, Any]:
    """Dispatch ``raopbridge <sub-command> …`` to the appropriate handler.

    Sub-commands:
    - ``activate`` — activate the plugin launching raop executable.
    - ``config``  — generate configuration file for the raop executable: the plugin must be de-activated.
    - ``deactivate``  — deactivate the plugin stopping the raop executable.
    - ``restart``  — restart the plugin using stored settings.
    - ``save``  — update and save current plugin settings.
    """
    if _raop_bridge is None:
        return {'error': 'RaopBridge plugin not initialized'}

    sub = str(command[1]).lower() if len(command) > 1 else ""

    match sub:
        case 'activate':
            return await _activate(ctx, command)
        case 'config':
            return await _raop_config(ctx, command)
        case 'deactivate':
            return await _deactivate(ctx, command)
        case 'restart':
            return await _restart(ctx, command)
        case 'save':
            return await _save_settings(ctx, command)
        case _:
            return {'error': f'Unknown raopbridge sub-command: {sub}'}


# ---------------------------------------------------------------------------
# JSON-RPC command dispatcher
# ---------------------------------------------------------------------------


async def _activate(
    ctx: CommandContext, command: list[Any]
) -> dict[str, Any]:
    _raop_bridge.activate_bridge()

    result: dict[str, Any] = {
        'result':  _raop_bridge.is_active,
    }
    return result


async def _raop_config(
    ctx: CommandContext, command: list[Any]
) -> dict[str, Any]:
    if _raop_bridge.is_active:
        return {
            'error': 'The bridge is active: deactivate it to generate a configuration file'
        }
    result: dict[str, Any] = {
        'result':  _raop_bridge.generate_config(),
    }
    return result


async def _deactivate(
    ctx: CommandContext, command: list[Any]
) -> dict[str, Any]:
    _raop_bridge.deactivate_bridge()

    result: dict[str, Any] = {
        'result':  _raop_bridge.is_active,
    }
    return result


async def _restart(
    ctx: CommandContext, command: list[Any]
) -> dict[str, Any]:
    """ use the stored settings to restart the plugin call ``save`` before to use the current settings"""
    global _raop_bridge

    settings_path = Path(_raop_bridge.data_dir) / SETTINGS_FILE
    await _raop_bridge.close()
    _raop_bridge = RaopBridge.from_settings(settings_path)
    await _raop_bridge.start()

    result: dict[str, Any] = {
        'active':  _raop_bridge.is_active,
    }
    return result


async def _save_settings(
    ctx: CommandContext, command: list[Any]
) -> dict[str, Any]:
    """ the command argument is a list with first the plugin name and the command followed by
        an arbitrary number of strings in the format key=value to update the settings
    """
    errors = []
    valid_keys = _raop_bridge.settings.keys()
    for value in command[2:]:
        setting = value.split('=', 1)
        if setting[0] in valid_keys:
            setattr(_raop_bridge, setting[0], setting[1])
        else:
            errors.append(f'Invalid setting name: \'{value}\'')
    if errors:
        return {
            'errors': ','.join(errors)
        }
    store_path = Path(_raop_bridge.data_dir) / SETTINGS_FILE
    save_settings(_raop_bridge.settings, store_path)

    result: dict[str, Any] = {
        'result':  True,
    }
    return result
