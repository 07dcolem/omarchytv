#!/usr/bin/env python3
"""Writes docs/vectors.json: fixed-input vectors the Java side must reproduce."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from omarchy_link import crypto as c  # noqa: E402


def vectors() -> dict:
    code, pc_id, tv_id = "123456", "0123456789abcdef0123456789abcdef", "fedcba9876543210fedcba9876543210"
    x = int.from_bytes(c.sha256(b"vector x"), "big")
    y = int.from_bytes(c.sha256(b"vector y"), "big")
    a = c.PcPairing(code, pc_id, x=x)
    b = c.TvPairing(code, tv_id, pc_id, a.message(), y=y)
    keys = a.finish(tv_id, b.message())
    body = b'{"key":"home"}'
    auth, nonce = c.sign_request(keys.token, pc_id, "POST", "/v1/remote/key", body, 1790000000, "AAAAAAAAAAAAAAAAAAAAAA")
    resp_body = b'{"ok":true}'
    ks = c.ws_session_key(keys.token, nonce, "BBBBBBBBBBBBBBBBBBBBBB")
    frame = c.seal_message(ks, b'{"seq":1,"type":"hello","data":{}}')
    return {
        "group": {"p": c.P_HEX.lower(), "g": 2, "M": f"{c.M:0512x}", "N": f"{c.N:0512x}"},
        "pairing": {
            "code": code, "pcId": pc_id, "tvId": tv_id, "x": f"{x:064x}", "y": f"{y:064x}",
            "w": f"{a.w:064x}", "T": c.b64u(a.message()), "S": c.b64u(b.message()),
            "ttHash": keys.tt_hash.hex(), "confirmPc": c.b64u(keys.confirm_pc),
            "confirmTv": c.b64u(keys.confirm_tv), "token": c.b64u(keys.token),
        },
        "request": {"method": "POST", "target": "/v1/remote/key", "ts": 1790000000, "nonce": nonce,
                    "body": body.decode(), "authorization": auth,
                    "responseStatus": 200, "responseBody": resp_body.decode(),
                    "xOtvSig": c.sign_response(keys.token, nonce, 200, resp_body)},
        "websocket": {"clientNonce": nonce, "serverNonce": "BBBBBBBBBBBBBBBBBBBBBB",
                      "sessionKey": ks.hex(), "frame": frame},
    }


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "docs" / "vectors.json"
    out.write_text(json.dumps(vectors(), indent=2) + "\n")
    print(f"wrote {out}")
