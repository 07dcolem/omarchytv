"""Menus and output in the Omarchy style: Walker (dmenu) > gum > plain, colours from the active theme."""
import os, re, shutil, subprocess
from pathlib import Path

THEME = Path.home() / ".config/omarchy/current/theme/colors.toml"


def colors() -> dict:
    out = {"accent": "#7aa2f7", "foreground": "#c0caf5", "background": "#1a1b26"}
    try:
        for line in THEME.read_text().splitlines():
            m = re.match(r'\s*([a-z_0-9]+)\s*=\s*"(#[0-9a-fA-F]{6})"', line)
            if m:
                out[m.group(1)] = m.group(2)
    except OSError:
        pass
    return out


def choose(prompt: str, items: list[str]) -> str | None:
    data = "\n".join(items)
    if shutil.which("walker") and os.environ.get("WAYLAND_DISPLAY"):
        r = subprocess.run(["walker", "--dmenu", "--width", "295", "--minheight", "1", "--maxheight", "630", "-p", prompt],
                           input=data, text=True, capture_output=True)
        return r.stdout.strip() or None
    if shutil.which("gum"):
        r = subprocess.run(["gum", "choose", "--header", prompt, "--cursor.foreground", colors()["accent"], *items],
                           text=True, stdout=subprocess.PIPE)
        return r.stdout.strip() or None
    for i, it in enumerate(items, 1):
        print(f"{i}) {it}")
    s = input(prompt + " ")
    return items[int(s) - 1] if s.isdigit() and 0 < int(s) <= len(items) else None


def ask(prompt: str) -> str:
    if shutil.which("gum"):
        return subprocess.run(["gum", "input", "--placeholder", prompt], text=True, stdout=subprocess.PIPE).stdout.strip()
    return input(prompt + ": ").strip()


def confirm(prompt: str) -> bool:
    if shutil.which("gum"):
        return subprocess.run(["gum", "confirm", prompt]).returncode == 0
    return input(prompt + " [s/N] ").strip().lower() in ("s", "y", "si", "yes")


def say(msg: str):
    if shutil.which("gum"):
        subprocess.run(["gum", "style", "--foreground", colors()["accent"], msg])
    else:
        print(msg)


def notify(msg: str, urgency: str = "normal"):
    """notify-send (mako on Omarchy), like the omarchy-* scripts; silent without a notification daemon."""
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "-u", urgency, "-a", "OmarchyTV", "OmarchyTV", msg], capture_output=True)


def run(cmd: list[str], env=None) -> int:
    if cmd[0] == "omarchy-link" and not shutil.which(cmd[0]) and os.environ.get("OMARCHY_LINK_BIN"):
        cmd = [os.environ["OMARCHY_LINK_BIN"]] + cmd[1:]
    if not shutil.which(cmd[0]) and not os.path.isfile(cmd[0]):
        say(f"{cmd[0]} non trovato: installa il plugin omarchy-link.")
        return 1
    return subprocess.run(cmd, env=env).returncode
