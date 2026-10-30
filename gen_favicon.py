#!/usr/bin/env python3
"""파비콘 생성 — PIL/ImageMagick 없는 환경이라 stdlib(zlib)만으로 raw PNG 작성.
닻(anchor) 모양, 사이트 팔레트(--ink 슬레이트 배경 + --accent 세이프티 오렌지) 그대로 사용.
"""
import math
import struct
import zlib
from pathlib import Path

INK = (0x12, 0x16, 0x1c)
ACCENT = (0xff, 0x7a, 0x3d)

OUT_DIR = Path(__file__).parent


def dist_to_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def angle_in_range(ang, lo, hi):
    ang = ang % 360
    lo = lo % 360
    hi = hi % 360
    if lo <= hi:
        return lo <= ang <= hi
    return ang >= lo or ang <= hi


def make_anchor(size):
    s = size / 256.0
    cx, cy = size / 2, size / 2
    ring_c = (cx, cy - 86 * s)
    ring_r = 30 * s
    ring_w = 14 * s
    stem_w = 15 * s
    stem_top = (cx, cy - 58 * s)
    stem_bot = (cx, cy + 70 * s)
    bar_y = cy - 28 * s
    bar_half = 44 * s
    bar_w = 15 * s
    fluke_r = 54 * s
    fluke_w = 14 * s
    fl_c = (stem_bot[0] - fluke_r * 0.86, stem_bot[1] - fluke_r * 0.5)
    fr_c = (stem_bot[0] + fluke_r * 0.86, stem_bot[1] - fluke_r * 0.5)

    def painted(x, y):
        # 고리(ring) — 원 둘레
        if abs(math.hypot(x - ring_c[0], y - ring_c[1]) - ring_r) < ring_w / 2:
            return True
        # 축(shank)
        if dist_to_segment(x, y, stem_top[0], stem_top[1], stem_bot[0], stem_bot[1]) < stem_w / 2:
            return True
        # 가로대(crossbar)
        if dist_to_segment(x, y, cx - bar_half, bar_y, cx + bar_half, bar_y) < bar_w / 2:
            return True
        # 왼쪽/오른쪽 갈고리(flukes) — stem_bot에서 바깥쪽 위로 말려올라가는 원호
        dl = math.hypot(x - fl_c[0], y - fl_c[1])
        if abs(dl - fluke_r) < fluke_w / 2:
            ang = math.degrees(math.atan2(y - fl_c[1], x - fl_c[0]))
            if angle_in_range(ang, 28, 232):
                return True
        dr = math.hypot(x - fr_c[0], y - fr_c[1])
        if abs(dr - fluke_r) < fluke_w / 2:
            ang = math.degrees(math.atan2(y - fr_c[1], x - fr_c[0]))
            if angle_in_range(ang, -52, 152):
                return True
        return False

    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            px = ACCENT if painted(x + 0.5, y + 0.5) else INK
            row += bytes(px)
        rows.append(bytes([0]) + bytes(row))
    return b"".join(rows)


def write_png(size, path):
    raw = make_anchor(size)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw, 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    path.write_bytes(png)
    print(f"wrote {path} ({size}x{size})")


if __name__ == "__main__":
    write_png(32, OUT_DIR / "favicon-32.png")
    write_png(180, OUT_DIR / "favicon-180.png")
