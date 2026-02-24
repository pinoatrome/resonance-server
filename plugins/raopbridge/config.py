# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2.

from __future__ import annotations

from dataclasses import dataclass, field

from xml.etree.ElementTree import Element, fromstring as root_fromstring


@dataclass(frozen=True, slots=True)
class RaopCommonOptions:

    streambuf_size: int = 2097152
    output_size: int = 1764000
    enabled: bool = True
    codecs: list[str] = field(default_factory=lambda: ['aac', 'ogg', 'ops', 'ogf', 'flc', 'alc', 'wav', 'aif', 'pcm', 'mp3'])
    sample_rate: int = 96000
    resolution: str | None = None
    resample: bool = True
    resample_options: str | None = None
    player_volume: int = -1
    volume_mapping: list[tuple[int, int,]] = field(default_factory=lambda: [(-30,1,), (-15,50,), (0,100,)])
    volume_feedback: bool = True
    volume_mode: int = 2
    mute_on_pause: bool = True
    send_metadata: bool = True
    send_coverart: bool = True
    auto_play: bool = False
    idle_timeout: int = 30
    remove_timeout: bool = False
    alac_encode: bool = False
    encryption: bool = False
    read_ahead: int = 1000
    server: str = '?'


@dataclass(frozen=True, slots=True)
class RaopDevice:
    """A device managed by the bridge.
    Attributes are coming from raop config xml file:
    <device>
    <udn>100E0D1D1A01@Beoplay M3._raop._tcp.local</udn>
    <name>Beoplay-M3-28977299</name>
    <friendly_name>Beoplay-M3-28977299</friendly_name>
    <mac>aa:aa:d8:00:25:39</mac>
    <enabled>1</enabled>
    </device>
    """

    udn: str
    """Unique identifier (e.g. '100E0D1D1A01@Beoplay M3._raop._tcp.local')."""

    name: str
    """Display name as preferred by the user (e.g. 'Beoplay M3 Bathroom')."""

    friendly_name: str
    """Device name as configured in the device settings (e.g. 'Beoplay-M3-28977299')."""

    mac: str
    """Mac Address (e.g. 'aa:aa:d8:00:25:39')."""

    enabled: bool
    """1 for True, 0 for False"""


@dataclass(frozen=True, slots=True)
class RaopConfig:
    common: RaopCommonOptions | None = None
    interface: str = '?'
    slimproto_log: str = 'info'
    stream_log: str = 'warn'
    output_log: str = 'info'
    decode_log: str = 'warn'
    main_log: str = 'info'
    slimmain_log: str = 'info'
    raop_log: str = 'info'
    util_log: str = 'info'
    log_limit: int = -1
    migration: int = 3
    ports: list[str] | None = None
    devices: list[RaopDevice] | None = None


def parse_config(raw) -> RaopConfig:
    def parse_str(el: Element, tag: str) -> str | None:
        child = el.find(tag)
        if child is not None:
            return child.text

    def parse_array_str(el: Element, tag: str, sep=',') -> [str]:
        child = el.find(tag)
        value = child.text if child is not None else None
        return value.split(sep) if value else []

    def parse_int(el: Element, tag: str) -> int | None:
        child = el.find(tag)
        if child is not None:
            value = child.text
            return int(value) if value else None

    def parse_bool(el: Element, tag: str) -> bool | None:
        child = el.find(tag)
        if child is not None:
            value = child.text
            return value == '1'

    def parse_volume_mapping_value(value: str, sep: str) -> list[tuple[int, ...]]:
        values = [v.strip() for v in value.split(sep) if v]
        return [tuple(int(v) for v in value.split(':')) for value in values]

    def parse_volume_mapping(el: Element, tag: str, sep=',') -> list[tuple[int, int]]:
        """'-30:1, -15:50, 0:100' -> [(-30, 1,), (-15, 50,), (-15, 50,)]"""
        child = el.find(tag)
        return parse_volume_mapping_value(child.text, sep) if child is not None else []

    root = root_fromstring(raw)
    node = root.find('common')
    common = RaopCommonOptions(
        streambuf_size=parse_int(node, 'streambuf_size'),
        output_size=parse_int(node, 'output_size'),
        enabled=parse_bool(node, 'enabled'),
        codecs=parse_array_str(node, 'codecs'),
        sample_rate=parse_int(node, 'sample_rate'),
        resolution=parse_str(node, 'resolution'),
        resample=parse_bool(node, 'resample'),
        resample_options=parse_str(node, 'resample_options'),
        player_volume=parse_int(node, 'player_volume'),
        volume_mapping=parse_volume_mapping(node, 'volume_mapping'),
        volume_feedback=parse_bool(node, 'volume_feedback'),
        volume_mode=parse_int(node, 'volume_mode'),
        mute_on_pause=parse_bool(node, 'mute_on_pause'),
        send_metadata=parse_bool(node, 'send_metadata'),
        send_coverart=parse_bool(node, 'send_coverart'),
        auto_play=parse_bool(node, 'auto_play'),
        idle_timeout=parse_int(node, 'idle_timeout'),
        remove_timeout=parse_bool(node, 'remove_timeout'),
        alac_encode=parse_bool(node, 'alac_encode'),
        encryption=parse_bool(node, 'encryption'),
        read_ahead=parse_int(node, 'read_ahead'),
        server=parse_str(node, 'server'),
    )

    devices: list[RaopDevice] = []
    for device in root.iter('device'):
        udn = parse_str(device, 'udn')
        name = parse_str(device, 'name')
        friendly_name = parse_str(device, 'friendly_name')
        mac = parse_str(device, 'mac')
        enabled = parse_bool(device, 'enabled')
        device = RaopDevice(udn=udn, name=name, friendly_name=friendly_name, mac=mac, enabled=enabled)
        devices.append(device)

    config = RaopConfig(
        devices=devices,
        common=common,
        interface=parse_str(root, 'interface'),
        slimproto_log=parse_str(root, 'slimproto_log'),
        stream_log=parse_str(root, 'stream_log'),
        output_log=parse_str(root, 'output_log'),
        decode_log=parse_str(root, 'decode_log'),
        main_log=parse_str(root, 'main_log'),
        slimmain_log=parse_str(root, 'slimmain_log'),
        raop_log=parse_str(root, 'raop_log'),
        util_log=parse_str(root, 'util_log'),
        log_limit=parse_int(root, 'log_limit'),
        migration=parse_int(root, 'migration'),
        ports=parse_array_str(root, 'ports'),
    )
    return config


def dump_config(config: RaopConfig) -> str:
    def format_str(value: str | None) -> str | None:
        return value or ''

    def format_array_str(values: [str], sep=',') -> str:
        return sep.join(values) if values else ''

    def format_int(value: int | None) -> str:
        return str(value) if value else ''

    def format_bool(value: bool | None) -> str:
        return '1' if value else '0'

    def format_volume_mapping_value(value: list[tuple[int, int]], sep: str) -> str:
        values = [f'{couple[0]}:{couple[1]}' for couple in value]
        return sep.join(values)

    def format_volume_mapping(value: list, sep=', ') -> str:
        """[(-30, 1,), (-15, 50,), (-15, 50,)] -> '-30:1, -15:50, 0:100'"""
        return format_volume_mapping_value(value, sep) if value else ''

    raw = f"""<?xml version="1.0"?>
<squeeze2raop>
<common>
<streambuf_size>{format_int(config.common.streambuf_size)}</streambuf_size>
<output_size>{format_int(config.common.output_size)}</output_size>
<enabled>{format_bool(config.common.enabled)}</enabled>
<codecs>{format_array_str(config.common.codecs)}</codecs>
<sample_rate>{format_int(config.common.sample_rate)}</sample_rate>
<resolution>{format_str(config.common.resolution)}</resolution>
<resample>{format_bool(config.common.resample)}</resample>
<resample_options>{format_str(config.common.resample_options)}</resample_options>
<player_volume>{format_int(config.common.player_volume)}</player_volume>
<volume_mapping>{format_volume_mapping(config.common.volume_mapping)}</volume_mapping>
<volume_feedback>{format_bool(config.common.volume_feedback)}</volume_feedback>
<volume_mode>{format_int(config.common.volume_mode)}</volume_mode>
<mute_on_pause>{format_bool(config.common.mute_on_pause)}</mute_on_pause>
<send_metadata>{format_bool(config.common.send_metadata)}</send_metadata>
<send_coverart>{format_bool(config.common.send_coverart)}</send_coverart>
<auto_play>{format_bool(config.common.auto_play)}</auto_play>
<idle_timeout>{format_int(config.common.idle_timeout)}</idle_timeout>
<remove_timeout>{format_bool(config.common.remove_timeout)}</remove_timeout>
<alac_encode>{format_bool(config.common.alac_encode)}</alac_encode>
<encryption>{format_bool(config.common.encryption)}</encryption>
<read_ahead>{format_int(config.common.read_ahead)}</read_ahead>
<server>{format_str(config.common.server)}</server>
</common>
<interface>{format_str(config.interface)}</interface>
<slimproto_log>{format_str(config.slimproto_log)}</slimproto_log>
<stream_log>{format_str(config.stream_log)}</stream_log>
<output_log>{format_str(config.output_log)}</output_log>
<decode_log>{format_str(config.decode_log)}</decode_log>
<main_log>{format_str(config.main_log)}</main_log>
<slimmain_log>{format_str(config.slimmain_log)}</slimmain_log>
<raop_log>{format_str(config.raop_log)}</raop_log>
<util_log>{format_str(config.util_log)}</util_log>
<log_limit>{format_int(config.log_limit)}</log_limit>
<migration>{format_int(config.migration)}</migration>
<ports>{format_array_str(config.ports)}</ports>
"""
    for device in config.devices:
        raw += f"""<device>
<udn>{format_str(device.udn)}</udn>
<name>{format_str(device.name)}</name>
<friendly_name>{format_str(device.friendly_name)}</friendly_name>
<mac>{format_str(device.mac)}</mac>
<enabled>{format_bool(device.enabled)}</enabled>
</device>
"""
    return raw + """</squeeze2raop>
"""

