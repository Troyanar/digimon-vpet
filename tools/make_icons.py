"""Erzeugt die App-Symbole (static/icons/) aus einem Digimon-Sprite.

Aufruf:  python tools/make_icons.py            (Standard: Agumon)
         python tools/make_icons.py 93         (anderes Digimon, z. B. Greymon)
"""
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LCD = (0xA9, 0xE4, 0xD9)
PIXEL = (0x06, 0x23, 0x2F)
FRAME = (0x06, 0x10, 0x31)
CYAN = (0x2E, 0xE6, 0xFF)


def png(width, height, rows):
    raw = b"".join(b"\x00" + bytes(v for px in row for v in px) for row in rows)
    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def icon(size, sprite):
    """Dunkler Rahmen, cyan Kante, LCD-Fläche mit dem Sprite in der Mitte."""
    rows = [[FRAME] * size for _ in range(size)]
    border, edge = size // 10, max(2, size // 64)
    for y in range(border - edge, size - border + edge):
        for x in range(border - edge, size - border + edge):
            rows[y][x] = CYAN
    for y in range(border, size - border):
        for x in range(border, size - border):
            rows[y][x] = LCD
    inner = size - 2 * border
    scale = int(inner * 0.75) // 16
    off = border + (inner - 16 * scale) // 2
    for sy, line in enumerate(sprite):
        for sx, bit in enumerate(line):
            if bit == "1":
                for y in range(off + sy * scale, off + (sy + 1) * scale):
                    for x in range(off + sx * scale, off + (sx + 1) * scale):
                        rows[y][x] = PIXEL
    return png(size, size, rows)


def main():
    dex = sys.argv[1] if len(sys.argv) > 1 else "29"
    data = json.loads((ROOT / "data" / "digimon.json").read_text(encoding="utf8"))
    sprite = [row for row in data["digimon"][dex]["frames"][0]]
    sprite = [row[::-1] for row in sprite]          # nach rechts schauen
    out = ROOT / "static" / "icons"
    out.mkdir(exist_ok=True)
    for size in (180, 192, 512):
        (out / f"icon-{size}.png").write_bytes(icon(size, sprite))
    print(f"Symbole mit {data['digimon'][dex]['name']} -> {out}")


if __name__ == "__main__":
    main()
