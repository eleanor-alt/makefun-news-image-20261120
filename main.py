#!/usr/bin/env python3
"""news-image-20261120: one image summing up the world news of
Friday 20 November 2026.

Dependency-free Python 3 (standard library only): a flat RGB pixel
buffer, a hand-written 5x7 bitmap font, simple shape drawing, and a
hand-rolled PNG encoder. No network, no clock, no randomness, so two
runs produce byte-identical output.

Writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ------------------------------------------------------------------ palette
NAVY = (16, 36, 60)
NAVY2 = (24, 52, 84)
CREAM = (248, 245, 236)
PAPER = (255, 253, 247)
INK = (22, 22, 26)
RED = (196, 24, 44)
GOLD = (206, 150, 28)
TEAL = (18, 120, 110)
GREY = (168, 160, 146)
LIGHT = (232, 228, 218)
SKY = (88, 138, 178)

# ------------------------------------------------------------------ 5x7 font
# Glyphs written for this entry: 7 rows of 5 cells, '#' = filled.
# Only the characters this image actually uses are defined; anything
# else falls back to a blank.
GLYPHS = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "&": (" ##  ", "#  # ", "#  # ", " #   ", "# # #", "#  # ", " ## #"),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
}


def glyph_width(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(buf, x, y, s, scale, color):
    """Draw text in the font above; unknown chars render as space."""
    cx = x
    for ch in s:
        g = GLYPHS.get(ch.upper(), GLYPHS[" "])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == "#":
                    fill(buf, cx + c * scale, y + r * scale,
                         scale, scale, color)
        cx += 6 * scale
    return cx


def wrap_to(s, scale, max_w):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
def new_buf():
    return bytearray(CREAM * (W * H))


def _px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(color)


def fill(buf, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        buf[(yy * W + x0) * 3:(yy * W + x1) * 3] = row


def line(buf, x0, y0, x1, y1, color, thick=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err, x, y = dx - dy, x0, y0
    while True:
        fill(buf, x, y, thick, thick, color)
        if x == x1 and y == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def disc(buf, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                _px(buf, xx, yy, color)


def tri(buf, p0, p1, p2, color):
    (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
    for yy in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
        xs = []
        for (ax, ay), (bx, by) in ((p0, p1), (p1, p2), (p2, p0)):
            if ay == by:
                continue
            if min(ay, by) <= yy <= max(ay, by):
                xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
        if len(xs) >= 2:
            a, b = int(min(xs)), int(max(xs))
            fill(buf, a, yy, b - a + 1, 1, color)


# ------------------------------------------------------------------ pictograms
# Each icon is drawn in a ~72x72 box at (x, y); all shapes are my own.

def icon_scales(buf, x, y):
    # Scales of justice: central post, beam, two pans.
    line(buf, x + 36, y + 6, x + 36, y + 56, NAVY, 3)
    line(buf, x + 8, y + 14, x + 64, y + 14, NAVY, 3)
    for px in (x + 8, x + 64):
        line(buf, px, y + 14, px - 6, y + 34, NAVY, 2)
        line(buf, px, y + 14, px + 6, y + 34, NAVY, 2)
        tri(buf, (px - 10, y + 34), (px + 10, y + 34), (px, y + 46), GOLD)
    fill(buf, x + 22, y + 56, 28, 5, NAVY)
    fill(buf, x + 30, y + 4, 12, 5, RED)


def icon_blast(buf, x, y):
    # Explosion star over a broken bridge span.
    cx, cy = x + 36, y + 26
    for ang in range(8):
        import math
        a = ang * math.pi / 4
        line(buf, int(cx + 10 * math.cos(a)), int(cy + 10 * math.sin(a)),
             int(cx + 30 * math.cos(a)), int(cy + 30 * math.sin(a)), RED, 4)
    disc(buf, cx, cy, 11, GOLD)
    disc(buf, cx, cy, 5, RED)
    line(buf, x + 4, y + 58, x + 30, y + 58, NAVY, 5)
    line(buf, x + 44, y + 58, x + 68, y + 58, NAVY, 5)
    line(buf, x + 30, y + 58, x + 37, y + 66, NAVY, 3)
    line(buf, x + 44, y + 58, x + 37, y + 66, NAVY, 3)


def icon_tower(buf, x, y):
    # Skyscraper with a missile streak crossing it.
    fill(buf, x + 24, y + 8, 24, 56, NAVY)
    for yy in range(y + 14, y + 56, 10):
        fill(buf, x + 28, yy, 16, 4, CREAM)
    fill(buf, x + 20, y + 64, 32, 4, NAVY)
    line(buf, x + 4, y + 18, x + 52, y + 44, RED, 4)
    disc(buf, x + 56, y + 46, 6, RED)
    disc(buf, x + 8, y + 12, 3, GOLD)
    disc(buf, x + 60, y + 10, 3, GOLD)


def icon_fall(buf, x, y):
    # Falling bars with a downward arrow: markets sliding.
    for i, h in enumerate((44, 32, 20)):
        fill(buf, x + 8 + i * 18, y + 56 - h, 12, h, SKY)
    line(buf, x + 6, y + 10, x + 30, y + 30, RED, 4)
    line(buf, x + 30, y + 30, x + 58, y + 52, RED, 4)
    tri(buf, (x + 58, y + 52), (x + 48, y + 48), (x + 58, y + 38), RED)


def icon_leaf(buf, x, y):
    # A leaf with a crossed-out flame: fossil phase-out dropped.
    tri(buf, (x + 36, y + 6), (x + 14, y + 40), (x + 58, y + 40), TEAL)
    tri(buf, (x + 36, y + 66), (x + 14, y + 40), (x + 58, y + 40), TEAL)
    line(buf, x + 36, y + 6, x + 36, y + 66, CREAM, 2)
    line(buf, x + 10, y + 58, x + 62, y + 14, RED, 5)


def icon_flags(buf, x, y):
    # Two crossed flagpoles with pennants: a summit deal.
    line(buf, x + 14, y + 10, x + 30, y + 60, NAVY, 3)
    line(buf, x + 58, y + 10, x + 42, y + 60, NAVY, 3)
    tri(buf, (x + 14, y + 10), (x + 40, y + 18), (x + 14, y + 26), TEAL)
    tri(buf, (x + 58, y + 10), (x + 32, y + 18), (x + 58, y + 26), GOLD)
    fill(buf, x + 22, y + 60, 28, 4, NAVY)


def icon_cross(buf, x, y):
    # Medical cross in a ring: an outbreak beaten.
    disc(buf, x + 36, y + 34, 30, TEAL)
    fill(buf, x + 30, y + 14, 12, 40, CREAM)
    fill(buf, x + 16, y + 28, 40, 12, CREAM)


ICONS = {
    "scales": icon_scales,
    "blast": icon_blast,
    "tower": icon_tower,
    "fall": icon_fall,
    "leaf": icon_leaf,
    "flags": icon_flags,
    "cross": icon_cross,
}

# ------------------------------------------------------------------ stories
# Verified Friday 20 November 2026 headlines (see task brief).
LEAD = ("JUSTICE - THE HAGUE",
        "ICJ: MYANMAR COMMITTED GENOCIDE",
        "AGAINST THE ROHINGYA - 9-6, FIRST SUCH RULING",
        "scales")

STORIES = [
    ("WAR", "blast",
     "KYIV BRIDGES HIT",
     "RUSSIAN STRIKES KILL NINE"),
    ("MIDDLE EAST", "tower",
     "RIYADH TOWER HIT",
     "HOUTHI MISSILE DAMAGES PIF TOWER"),
    ("MARKETS", "fall",
     "MARKETS SLIDE",
     "S&P DOWN 2%, NIKKEI DOWN 4.8%"),
    ("CLIMATE", "leaf",
     "COP31 DROPS FOSSIL PHASE-OUT",
     "DRAFT IN ANTALYA OMITS THE CALL"),
    ("EUROPE", "flags",
     "EU-UK SUMMIT DEAL",
     "TRADE, ENERGY, YOUTH MOBILITY"),
    ("HEALTH", "cross",
     "KENYA BEATS EBOLA",
     "LAST PATIENT OUT, 42-DAY COUNTDOWN"),
]

FOOTER_ITEMS = [
    "ALSO: CYCLONE AKVAN HITS ODISHA",
    "GTA VI: $3.79BN IN DAY ONE",
    "US SENATE PASSES ENERGY BILL 62-33",
    "MERZ REJECTS A NEW YALTA DEAL",
]


def render():
    buf = new_buf()

    # --- header band: the date is the biggest thing on the page.
    fill(buf, 0, 0, W, 148, NAVY)
    fill(buf, 0, 148, W, 6, RED)
    title = "THE WORLD IN ONE DAY"
    draw_text(buf, (W - text_w(title, 4)) // 2, 22, title, 4, CREAM)
    date = "FRIDAY 20 NOVEMBER 2026"
    draw_text(buf, (W - text_w(date, 6)) // 2, 76, date, 6, GOLD)

    # --- lead story: full-width panel with a red left bar.
    lx, ly, lw, lh = 32, 172, W - 64, 158
    fill(buf, lx, ly, lw, lh, PAPER)
    fill(buf, lx, ly, 10, lh, RED)
    draw_text(buf, lx + 28, ly + 16, LEAD[0], 3, RED)
    draw_text(buf, lx + 28, ly + 52, LEAD[1], 4, INK)
    draw_text(buf, lx + 28, ly + 104, LEAD[2], 3, NAVY2)
    ICONS[LEAD[3]](buf, lx + lw - 108, ly + 40)

    # --- story grid: 2 columns x 3 rows.
    gx, gy = 32, 348
    col_w, row_h, gap = 468, 168, 24
    for i, (kicker, icon, head, sub) in enumerate(STORIES):
        cx = gx + (i % 2) * (col_w + gap)
        cy = gy + (i // 2) * (row_h + 16)
        fill(buf, cx, cy, col_w, row_h, PAPER)
        fill(buf, cx, cy, col_w, 3, TEAL if i % 2 else NAVY2)
        draw_text(buf, cx + 16, cy + 16, kicker, 2, RED)
        for j, ln in enumerate(wrap_to(head, 3, col_w - 116)):
            draw_text(buf, cx + 16, cy + 48 + j * 26, ln, 3, INK)
        for j, ln in enumerate(wrap_to(sub, 2, col_w - 32)):
            draw_text(buf, cx + 16, cy + 118 + j * 20, ln, 2, NAVY2)
        ICONS[icon](buf, cx + col_w - 88, cy + 34)

    # --- footer strip: the smaller stories, one per line.
    fy = 348 + 3 * row_h + 2 * 16 + 18
    fill(buf, 0, fy, W, 4, RED)
    for i, item in enumerate(FOOTER_ITEMS):
        fx = 40 + (i % 2) * 500
        fy2 = fy + 16 + (i // 2) * 22
        draw_text(buf, fx, fy2, item, 2, INK)
    foot = "FRIDAY 20 NOVEMBER 2026 - ONE IMAGE, ONE DAY"
    draw_text(buf, (W - text_w(foot, 2)) // 2, H - 26, foot, 2, GREY)
    return bytes(buf)


# ------------------------------------------------------------------ PNG writer
def png_bytes(px):
    raw = b"".join(b"\x00" + px[r * W * 3:(r + 1) * W * 3]
                   for r in range(H))

    def chunk(tag, data):
        body = struct.pack(">I", len(data)) + tag + data
        return body + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png_bytes(render()))


if __name__ == "__main__":
    main()
