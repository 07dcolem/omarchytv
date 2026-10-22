"""LAN-only guard: the PC never talks to a TV outside private/link-local ranges."""

from __future__ import annotations

import ipaddress
import json
import shutil
import subprocess


def is_lan_address(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host.split("%", 1)[0])
    except ValueError:
        return False
    if ip.is_loopback:
        return True  # the mock TV and tests
    if ip.version == 4:
        return ip.is_private and not ip.is_multicast and not ip.is_unspecified
    return ip.is_link_local or ip in ipaddress.ip_network("fc00::/7")


def local_networks() -> list:
    """Networks of this PC's interfaces (from `ip -j addr`); empty if unknown."""
    if not shutil.which("ip"):
        return []
    try:
        out = subprocess.run(["ip", "-j", "addr"], capture_output=True, text=True, timeout=3).stdout
        nets = []
        for iface in json.loads(out or "[]"):
            for a in iface.get("addr_info", []):
                try:
                    nets.append(ipaddress.ip_interface(f"{a['local']}/{a['prefixlen']}").network)
                except (KeyError, ValueError):
                    pass
        return nets
    except (OSError, ValueError, subprocess.SubprocessError):
        return []


def on_local_subnet(host: str) -> bool | None:
    """True/False when the PC's interfaces are known, None when they are not."""
    nets = local_networks()
    if not nets:
        return None
    try:
        ip = ipaddress.ip_address(host.split("%", 1)[0])
    except ValueError:
        return False
    return ip.is_loopback or any(ip in n for n in nets if n.version == ip.version)


def check_host(host: str, strict_subnet: bool = True) -> None:
    if not is_lan_address(host):
        raise ValueError(f"{host} is not a LAN address; Omarchy Link only talks to the local network")
    if strict_subnet and on_local_subnet(host) is False:
        raise ValueError(
            f"{host} is not on a subnet of this PC; set \"allowOtherSubnets\": true in config.json "
            "if your TV is on another LAN segment"
        )
