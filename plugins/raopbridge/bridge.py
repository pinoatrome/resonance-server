# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

from __future__ import annotations

import os
import subprocess
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import (
    RaopConfig, RaopCommonOptions, RaopDevice, dump_config
)

logger = logging.getLogger(__name__)

PLUGIN_NAME = 'raopbridge'
SETTINGS_FILE = 'raopbridge.json'


def define_valid_bin() -> [str]:
    import platform
    system = platform.system()
    machine = platform.machine()
    if system == 'Darwin':
        if machine == 'arm64':
            return ['squeeze2raop-macos-arm64-static', 'squeeze2raop-macos-arm64']
        if machine == 'x86_64':
            return ['squeeze2raop-macos-x86_64-static', 'squeeze2raop-macos-x86_64']
        return ['squeeze2raop-macos-static', 'squeeze2raop-macos']
    if system == 'FreeBSD':
        return ['squeeze2raop-freebsd-x86_64-static', 'squeeze2raop-freebsd-x86_64']
    if system == 'Windows':
        return ['squeeze2raop-static.exe', 'squeeze2raop.exe']
    if system == 'Linux':
        if machine == 'x86_64':
            return ['squeeze2raop-linux-x86_64-static', 'squeeze2raop-linux-x86_64']
        if machine == 'i386':
            return ['squeeze2raop-linux-x86-static', 'squeeze2raop-linux-x86']
        if machine == 'aarch64':
            return ['squeeze2raop-linux-aarch64-static', 'squeeze2raop-linux-aarch64']
        if machine == 'arm':
            return ['squeeze2raop-linux-arm-static', 'squeeze2raop-linux-arm', 'squeeze2raop-linux-armv6-static',
                    'squeeze2raop-linux-armv6', 'squeeze2raop-linux-armv5-static', 'squeeze2raop-linux-armv5']
        if machine == 'powerpc':
            return ['squeeze2raop-linux-static', 'squeeze2raop-linux-powerpc']
        if machine == 'sparc':
            return ['squeeze2raop-linux-sparc64-static', 'squeeze2raop-linux-sparc64']
        if machine == 'mips':
            return ['squeeze2raop-linux-mips-static', 'squeeze2raop-linux-mips']
    logger.warning(f'unable to define any executable for squeeze2raop: unsupported platform: {system} {machine}')
    return []


def default_settings(**kwargs: dict[str, Any]) -> dict[str, Any]:
    valid_bin_array = define_valid_bin()
    return {
        'bin': valid_bin_array[0] if valid_bin_array else None,
        'interface': kwargs.pop('interface', '127.0.0.1'),
        'server': kwargs.pop('server', '?'),
        'active_at_startup': kwargs.pop('active_at_startup', True),
        **kwargs
    }


def format_server_setting(**kwargs) -> str:
    try:
        port = kwargs['port']
        host = kwargs['host']
        if host == '0.0.0.0':
            host = '127.0.0.1'
        return f"{host}:{port}"
    except KeyError:
        return '?'


def load_settings(path: Path) -> dict[str, Any]:
    import json
    with open(path, 'r', encoding='utf-8') as config_file:
        prefs = json.load(config_file)
    return dict(prefs)


def save_settings(settings: dict[str, Any], path: Path) -> None:
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, 'w', encoding='utf-8') as configfile:
        configfile.write(json.dumps(settings, indent=2, ensure_ascii=False))
    tmp.replace(path)    # Atomic rename


def read_squeeze2raop_config(config_path: Path) -> RaopConfig:
    from .config import parse_config
    with open(str(config_path), 'r') as fp:
        raw = fp.read()
    return parse_config(raw)


def check_valid_bin(path: Path | None) -> None:
    if path is None:
        raise RuntimeError('No binary selected for squeeze2raop: check settings')
    if not path.is_file():
        raise RuntimeError(f'Invalid value for squeeze2raop: unable to find "{path}"')
    if not os.access(path, os.X_OK):
        raise RuntimeError(f'Invalid value for squeeze2raop: unable to execute "{path}"')


def build_path_bin(value):
    """The binaries are installed in the plugins directory of the server"""
    return Path('plugins') / PLUGIN_NAME / 'lib' / value if value else None


def identify_renderers(executable: Path, args: [str] = None, config_path: Path = None, timeout: int = None) -> int:
    """
    Execute 'squeeze2raop-macos-arm64-static' library in interactive mode to save the config file and exit

    Note:
        the invoked file in lib must be flagged as executable
        `chmod u+x squeeze2raop-macos-arm64-static`
    """

    process_args = [str(executable)]
    if config_path:
        process_args += ['-x', str(config_path)]
    if args:
        process_args += args
    command = f'save {config_path}\nexit\n'.encode('utf-8')
    try:
        value = subprocess.run(process_args, input=command, timeout=timeout or 30, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=False).stdout
        logger.debug(f'{executable} returned {value}')
        return int.from_bytes(value)
    except subprocess.TimeoutExpired as e:
        logger.warning(f'{executable} timed out: {e}')
        return -1


def call_executable(*args, **kwargs):
    return subprocess.Popen(*args, **kwargs)


@dataclass
class RaopBridge:
    bin: str
    interface: str
    server: str
    active_at_startup: bool = field(init=True, default=False)
    config: str = 'squeeze2raop.xml'
    auto_save: bool = True
    logging_enabled: bool = True
    debug_enabled: bool = False
    debug_category: str = 'all'
    debug_level: str = 'info'
    logging_file: str = 'squeeze2raop.log'
    pid_file: str = 'squeeze2raop.pid'
    data_dir: str = field(init=True, kw_only=True)
    raop_config: RaopConfig | None = field(init=False, default=None, kw_only=True)
    bridge_process: subprocess.Popen | None = field(init=False, default=None, kw_only=True)

    @classmethod
    def from_settings(cls, path: Path, **kwargs):
        logger.debug(f'Loading settings from {path}')
        options = load_settings(path)
        if kwargs:
            options.update(**kwargs)
        options['data_dir'] = str(path.parent)
        instance = RaopBridge(**options)
        logger.info(f'Loaded plugin from {path}')
        return instance

    @property
    def settings(self) -> dict[str, Any]:
        """ the plugin settings can be stored in its settings file"""
        prefs = self.__dict__.copy()
        for attr in ['bridge_process', 'data_dir', 'raop_config']:
            if attr in prefs:
                del prefs[attr]
        return prefs

    @property
    def is_active(self):
        """ the plugin is active when the bridge executable is running """
        return self.bridge_process.poll() is None if self.bridge_process else False

    async def start(self) -> None:
        """ load the plugin preferences and the bridge configuration
        a) the bin program file must be:
         - selected (the preferences contains one of the available binaries for the O.S.)
         - valid (the name in the preferences is actually a file present in the lib dir of the plugin)
         - executable (the file must be executable)
        b) launches the bridge in a non-interactive mode using -Z option
        """
        logger.debug(f'checking bin value {self.bin}')
        bin_path = build_path_bin(self.bin)
        check_valid_bin(bin_path)
        config_path = Path(self.data_dir) / self.config
        if config_path.is_file():
            logger.debug(f'bridge executable using config from {config_path}')
        else:
            logger.info(f'no raop config file: the bridge will create it (if autosave is enabled) in {config_path}')
        logger.debug('RaopBridge started inactive - bridge will be active (if autostart) after server started event')

    async def activate_bridge(self) -> None:
        if self.is_active:
            logger.warning(f'bridge is already active')
            return
        if self.bridge_process:
            logger.warning(f'activate_bridge: kill dead bridge with return code: {self.bridge_process.returncode}')
            self.deactivate_bridge()
        bin_path = build_path_bin(self.bin)
        args = self.build_bin_args()
        logger.debug(f'starting {bin_path} {" ".join(args)}')
        self.bridge_process = call_executable(executable=bin_path, args=args, shell=True)
        logger.debug('bridge process started')

    def deactivate_bridge(self) -> None:
        if self.bridge_process:
            logger.debug('deactivating bridge')
            self.bridge_process.kill()
            self.bridge_process = None

    def build_bin_args(self, interactive=None):
        args = '' if interactive else '-Z'
        if self.auto_save:
            args += ' -I'
        if self.pid_file:
            pid_path = Path(self.data_dir) / self.pid_file
            args += f' -p {pid_path}'
        if self.interface:
            args += f' -b {self.interface}'
        if self.server:
            args += f' -s {self.server}'
        if self.logging_enabled:
            logging_path = Path(self.data_dir) / self.logging_file
            args += f' -f {logging_path}'
            logger.debug(f'logging to {logging_path}')
            if self.debug_enabled:
                logger.debug(f'debugging {self.debug_category}={self.debug_level}')
                args += f' -d {self.debug_category}={self.debug_level}'
        if self.config:
            config_path = Path(self.data_dir) / self.config
            args += f' -x {config_path}'
        return args.split(' ')

    def save_config(self, raop_config, timestamp=None):
        config_path = Path(self.data_dir) / self.config
        if timestamp is not None:
            file_mod_time = os.stat(config_path).st_mtime
            if timestamp < file_mod_time:
                raise ValueError(f'configuration file modified: reload')
        config_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = config_path.with_suffix(".tmp")
        with open(tmp, 'w', encoding='utf-8') as configfile:
            configfile.write(dump_config(raop_config))
        tmp.replace(config_path)  # Atomic rename

    def generate_config(self) -> bool:
        logging.info(f'generating bridge config file {self.config}')
        args = self.build_bin_args(interactive=True)
        bin_path = build_path_bin(self.bin)
        logging.debug(f'executing {bin_path} {" ".join(args)}')
        return_value = identify_renderers(bin_path, args=args)
        return return_value == 0

    async def parse_common_options(self) -> RaopCommonOptions | None:
        """the common options for devices are in the config"""
        config_path = Path(self.data_dir) / self.config
        raop_config = read_squeeze2raop_config(config_path)
        return raop_config.common

    async def parse_devices(self) -> list[RaopDevice] | None:
        """the discovered devices are in the config"""
        config_path = Path(self.data_dir) / self.config
        raop_config = read_squeeze2raop_config(config_path)
        return raop_config.devices

    async def save_device(self, device: RaopDevice) -> None:
        """add or updates the device in the bridge configuration file"""
        config_path = Path(self.data_dir) / self.config
        raop_config = read_squeeze2raop_config(config_path)
        timestamp = time.time()
        index = -1
        for idx, item in enumerate(raop_config.devices):
            if item.udn == device.udn:
                index = idx
                break
        if index == -1:
            raop_config.devices.append(device)
        else:
            raop_config.devices[index] = device
        self.save_config(raop_config, timestamp=timestamp)

    async def remove_device(self, udn):
        config_path = Path(self.data_dir) / self.config
        raop_config = read_squeeze2raop_config(config_path)
        timestamp = time.time()
        index = -1
        for idx, item in enumerate(raop_config.devices):
            if item.udn == udn:
                index = idx
                break
        if index == -1:
            raise ValueError(f'Device not found {udn}')
        del raop_config.devices[index]
        self.save_config(raop_config, timestamp=timestamp)

    async def close(self) -> None:
        self.deactivate_bridge()
        logger.debug('RaopBridge closed')
