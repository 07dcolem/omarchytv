"""Tiny DNS-SD over mDNS (RFC 6762/6763): a one-shot browser and, for the mock
TV, a responder. Stdlib only, IPv4 only.

The browser sends a PTR query for _omarchytv._tcp.local from an ephemeral port,
so responders answer by unicast ("legacy unicast", RFC 6762 6.7). Android's
NsdManager and Avahi both do. OMARCHY_LINK_MDNS=host:port sends the query to a
single unicast address instead (used by the tests).
"""

from __future__ import annotations

import os
import random
import socket
import struct
import threading
import time

from . import SERVICE_TYPE

MDNS_ADDR = ("224.0.0.251", 5353)
T_A, T_PTR, T_TXT, T_SRV, T_ANY = 1, 12, 16, 33, 255


def encode_name(name: str) -> bytes:
    out = b""
    for label in name.rstrip(".").split("."):
        raw = label.encode("utf-8")[:63]
        out += bytes([len(raw)]) + raw
    return out + b"\x00"


def decode_name(data: bytes, off: int) -> tuple[str, int]:
    labels, jumped, end, hops = [], False, off, 0
    while True:
        if off >= len(data):
            raise ValueError("truncated name")
        n = data[off]
        if n & 0xC0 == 0xC0:
            ptr = ((n & 0x3F) << 8) | data[off + 1]
            if not jumped:
                end = off + 2
            jumped, off, hops = True, ptr, hops + 1
            if hops > 20:
                raise ValueError("compression loop")
            continue
        if n == 0:
            if not jumped:
                end = off + 1
            return ".".join(labels) + ".", end
        labels.append(data[off + 1: off + 1 + n].decode("utf-8", "replace"))
        off += 1 + n


def build_query(name: str, qtype: int, qid: int = 0) -> bytes:
    return struct.pack(">HHHHHH", qid, 0, 1, 0, 0, 0) + encode_name(name) + struct.pack(">HH", qtype, 1)


def parse_message(data: bytes) -> dict:
    qid, flags, qd, an, ns, ar = struct.unpack(">HHHHHH", data[:12])
    off, questions, records = 12, [], []
    for _ in range(qd):
        name, off = decode_name(data, off)
        qtype, qclass = struct.unpack(">HH", data[off: off + 4])
        off += 4
        questions.append((name.lower(), qtype))
    for _ in range(an + ns + ar):
        name, off = decode_name(data, off)
        rtype, rclass, ttl, rdlen = struct.unpack(">HHIH", data[off: off + 10])
        off += 10
        rd = data[off: off + rdlen]
        rec = {"name": name, "type": rtype, "ttl": ttl}
        if rtype == T_PTR:
            rec["target"] = decode_name(data, off)[0]
        elif rtype == T_SRV:
            rec["priority"], rec["weight"], rec["port"] = struct.unpack(">HHH", rd[:6])
            rec["target"] = decode_name(data, off + 6)[0]
        elif rtype == T_A and rdlen == 4:
            rec["address"] = socket.inet_ntoa(rd)
        elif rtype == T_TXT:
            txt, i = {}, 0
            while i < len(rd):
                n = rd[i]
                item = rd[i + 1: i + 1 + n].decode("utf-8", "replace")
                key, _, val = item.partition("=")
                if key:
                    txt[key.lower()] = val
                i += 1 + n
            rec["txt"] = txt
        records.append(rec)
        off += rdlen
    return {"id": qid, "flags": flags, "questions": questions, "records": records}


def _target() -> tuple[str, int]:
    override = os.environ.get("OMARCHY_LINK_MDNS", "")
    if override:
        host, _, port = override.rpartition(":")
        return host, int(port)
    return MDNS_ADDR


def browse(timeout: float = 2.0, service: str = SERVICE_TYPE) -> list[dict]:
    """Returns [{instance, name, id, host, address, port, txt}] for each TV that answered."""
    target = _target()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    sock.bind(("0.0.0.0", 0))
    qid = random.randint(1, 0xFFFF)
    records: list[dict] = []
    sources: dict[str, str] = {}
    try:
        sock.sendto(build_query(service, T_PTR, qid), target)
        deadline = time.monotonic() + timeout
        resent = False
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                break
            if not resent and left < timeout / 2:
                sock.sendto(build_query(service, T_PTR, qid), target)
                resent = True
            sock.settimeout(min(left, timeout / 2))
            try:
                data, src = sock.recvfrom(9000)
            except socket.timeout:
                continue
            try:
                msg = parse_message(data)
            except (ValueError, struct.error, IndexError):
                continue
            if not msg["flags"] & 0x8000:
                continue  # a query, not a response
            for rec in msg["records"]:
                rec["_src"] = src[0]
                records.append(rec)
    finally:
        sock.close()
    return _assemble(records, service)


def _assemble(records: list[dict], service: str) -> list[dict]:
    low = lambda s: s.lower()
    instances = {low(r["target"]) for r in records if r["type"] == T_PTR and low(r["name"]) == low(service)}
    srv = {low(r["name"]): r for r in records if r["type"] == T_SRV}
    txt = {low(r["name"]): r.get("txt", {}) for r in records if r["type"] == T_TXT}
    addr = {low(r["name"]): r["address"] for r in records if r["type"] == T_A and "address" in r}
    found = {}
    for inst in instances:
        s = srv.get(inst)
        if not s:
            continue
        t = txt.get(inst, {})
        src = next((r["_src"] for r in records if low(r["name"]) == inst), None)
        address = addr.get(low(s["target"])) or src
        label = inst[: -len(service) - 1] if inst.endswith(low(service)) else inst
        tv_id = t.get("id", "") or inst
        found[tv_id] = {
            "instance": inst,
            "name": t.get("name") or label,
            "id": t.get("id", ""),
            "host": s["target"],
            "address": address,
            "port": s["port"],
            "txt": t,
        }
    return sorted(found.values(), key=lambda d: d["name"])


# --------------------------------------------------------------- responder

def _rr(name: str, rtype: int, ttl: int, rdata: bytes, flush: bool = False) -> bytes:
    rclass = 0x8001 if flush else 1
    return encode_name(name) + struct.pack(">HHIH", rtype, rclass, ttl, len(rdata)) + rdata


class Responder:
    """Answers PTR/SRV/TXT/A queries for one service instance (mock TV only)."""

    def __init__(self, instance: str, port: int, txt: dict, address: str,
                 bind: tuple[str, int] = ("0.0.0.0", 5353), multicast: bool = True,
                 service: str = SERVICE_TYPE):
        self.service = service
        self.instance = f"{instance}.{service}"
        self.hostname = "omarchytv-mock.local."
        self.port, self.txt, self.address = port, txt, address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind(bind)
        self.bound = self.sock.getsockname()
        if multicast:
            mreq = socket.inet_aton(MDNS_ADDR[0]) + socket.inet_aton("0.0.0.0")
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> "Responder":
        self.thread.start()
        return self

    def close(self) -> None:
        self.stop.set()
        try:
            self.sock.close()
        except OSError:
            pass

    def answer(self, qid: int) -> bytes:
        txt = b"".join(
            bytes([len(item)]) + item
            for item in (f"{k}={v}".encode("utf-8")[:255] for k, v in self.txt.items())
        )
        srv = struct.pack(">HHH", 0, 0, self.port) + encode_name(self.hostname)
        answers = [
            _rr(self.service, T_PTR, 4500, encode_name(self.instance)),
            _rr(self.instance, T_SRV, 120, srv, True),
            _rr(self.instance, T_TXT, 4500, txt, True),
            _rr(self.hostname, T_A, 120, socket.inet_aton(self.address), True),
        ]
        return struct.pack(">HHHHHH", qid, 0x8400, 0, len(answers), 0, 0) + b"".join(answers)

    def _run(self) -> None:
        while not self.stop.is_set():
            try:
                self.sock.settimeout(0.5)
                data, src = self.sock.recvfrom(9000)
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                msg = parse_message(data)
            except (ValueError, struct.error, IndexError):
                continue
            if msg["flags"] & 0x8000:
                continue
            names = {self.service.lower(), self.instance.lower(), self.hostname.lower()}
            if not any(q[0] in names for q in msg["questions"]):
                continue
            reply = self.answer(msg["id"] if src[1] != 5353 else 0)
            try:
                self.sock.sendto(reply, src if src[1] != 5353 else MDNS_ADDR)
            except OSError:
                pass
