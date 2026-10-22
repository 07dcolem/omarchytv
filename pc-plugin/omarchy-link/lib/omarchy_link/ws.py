"""Minimal RFC 6455 framing over a blocking socket (text, ping, pong, close).

Shared by the PC client and the mock TV. No extensions, no fragmentation on
send; fragmented frames are reassembled on receive. Frames are capped at 1 MiB.
"""

from __future__ import annotations

import base64
import hashlib
import os
import socket
import struct

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
MAX_FRAME = 1 << 20

OP_CONT, OP_TEXT, OP_BIN, OP_CLOSE, OP_PING, OP_PONG = 0x0, 0x1, 0x2, 0x8, 0x9, 0xA


class Closed(ConnectionError):  # an OSError, so reconnect loops catch it
    pass


def accept_key(key: str) -> str:
    return base64.b64encode(hashlib.sha1((key + GUID).encode("ascii")).digest()).decode("ascii")


def new_key() -> str:
    return base64.b64encode(os.urandom(16)).decode("ascii")


def _recv_exact(sock: socket.socket, n: int, buf: bytearray) -> bytes:
    while len(buf) < n:
        chunk = sock.recv(max(4096, n - len(buf)))
        if not chunk:
            raise Closed("connection closed")
        buf.extend(chunk)
    out = bytes(buf[:n])
    del buf[:n]
    return out


class Conn:
    """One side of a WebSocket. mask=True for clients (RFC 6455 5.3)."""

    def __init__(self, sock: socket.socket, mask: bool, leftover: bytes = b""):
        self.sock = sock
        self.mask = mask
        self.buf = bytearray(leftover)
        self.closed = False

    def send(self, opcode: int, payload: bytes = b"") -> None:
        if self.closed and opcode != OP_CLOSE:
            raise Closed("closed")
        header = bytearray([0x80 | opcode])
        n = len(payload)
        bit = 0x80 if self.mask else 0
        if n < 126:
            header.append(bit | n)
        elif n < 65536:
            header.append(bit | 126)
            header += struct.pack(">H", n)
        else:
            header.append(bit | 127)
            header += struct.pack(">Q", n)
        if self.mask:
            key = os.urandom(4)
            header += key
            payload = bytes(b ^ key[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + payload)

    def send_text(self, text: str) -> None:
        self.send(OP_TEXT, text.encode("utf-8"))

    def _frame(self):
        b1, b2 = _recv_exact(self.sock, 2, self.buf)
        fin, opcode = b1 & 0x80, b1 & 0x0F
        masked, n = b2 & 0x80, b2 & 0x7F
        if n == 126:
            n = struct.unpack(">H", _recv_exact(self.sock, 2, self.buf))[0]
        elif n == 127:
            n = struct.unpack(">Q", _recv_exact(self.sock, 8, self.buf))[0]
        if n > MAX_FRAME:
            raise Closed("frame too large")
        key = _recv_exact(self.sock, 4, self.buf) if masked else None
        data = _recv_exact(self.sock, n, self.buf)
        if key:
            data = bytes(b ^ key[i % 4] for i, b in enumerate(data))
        return bool(fin), opcode, data

    def recv(self) -> str:
        """Next text message. Answers pings; raises Closed on close."""
        parts: list[bytes] = []
        while True:
            fin, opcode, data = self._frame()
            if opcode == OP_PING:
                self.send(OP_PONG, data)
                continue
            if opcode == OP_PONG:
                continue
            if opcode == OP_CLOSE:
                if not self.closed:
                    try:
                        self.send(OP_CLOSE, data[:2])
                    except OSError:
                        pass
                self.closed = True
                raise Closed("peer closed")
            if opcode in (OP_TEXT, OP_BIN, OP_CONT):
                parts.append(data)
                if sum(len(p) for p in parts) > MAX_FRAME:
                    raise Closed("message too large")
                if fin:
                    return b"".join(parts).decode("utf-8")

    def close(self) -> None:
        if not self.closed:
            try:
                self.send(OP_CLOSE, struct.pack(">H", 1000))
            except OSError:
                pass
        self.closed = True
        try:
            self.sock.close()
        except OSError:
            pass
