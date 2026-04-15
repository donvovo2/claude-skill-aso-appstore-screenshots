#!/usr/bin/env python3
"""
Generate Android (Google Pixel-style) device frame template PNG.
Output: assets/android_device_frame.png — standalone device image (not positioned on canvas).
compose.py positions this dynamically based on text height.

Google Pixel proportions: thin bezels, punch-hole camera centred at top,
power + volume buttons on the right side only.
"""

from PIL import Image, ImageDraw, ImageChops

# ── Device dimensions ───────────────────────────────────────────────
# Width is ~80% of 1080 canvas
DEVICE_W = 860
DEVICE_H = 1870           # tall enough to bleed off 1920 canvas
DEVICE_CORNER_R = 48
BEZEL = 12
SCREEN_CORNER_R = 40

# ── Punch-hole camera (Google Pixel style) ───────────────────────────
PH_DIAMETER = 22          # punch-hole circle diameter
PH_TOP = 15               # offset from top of screen area

SCREEN_W = DEVICE_W - 2 * BEZEL
SCREEN_H = DEVICE_H - 2 * BEZEL


def generate():
    frame = Image.new("RGBA", (DEVICE_W, DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body (dark grey outer, darker inner) ─────────────────
    fd.rounded_rectangle(
        [0, 0, DEVICE_W - 1, DEVICE_H - 1],
        radius=DEVICE_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, DEVICE_W - 2, DEVICE_H - 2],
        radius=DEVICE_CORNER_R - 1,
        fill=(20, 20, 20, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x = BEZEL
    screen_y = BEZEL

    cutout = Image.new("L", (DEVICE_W, DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + SCREEN_H],
        radius=SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Punch-hole camera (centred horizontally at top) ─────────────
    ph_x = (DEVICE_W - PH_DIAMETER) // 2
    ph_y = screen_y + PH_TOP
    ImageDraw.Draw(frame).ellipse(
        [ph_x, ph_y, ph_x + PH_DIAMETER, ph_y + PH_DIAMETER],
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons (right side only — Google Pixel layout) ────────
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)

    # Power button (right side, mid-height)
    fd2.rounded_rectangle(
        [DEVICE_W, 280, DEVICE_W + 4, 380],
        radius=2, fill=btn_color,
    )
    # Volume up (right side, above power)
    fd2.rounded_rectangle(
        [DEVICE_W, 160, DEVICE_W + 4, 240],
        radius=2, fill=btn_color,
    )
    # Volume down (right side, above power)
    fd2.rounded_rectangle(
        [DEVICE_W, 250, DEVICE_W + 4, 270],
        radius=2, fill=btn_color,
    )

    out = "assets/android_device_frame.png"
    frame.save(out, "PNG")
    print(f"Done: {out} ({DEVICE_W}x{DEVICE_H})")
    print(f"  BEZEL={BEZEL}, SCREEN_W={SCREEN_W}, SCREEN_H={SCREEN_H}")
    print(f"  SCREEN_CORNER_R={SCREEN_CORNER_R}, PUNCH_HOLE={PH_DIAMETER}px")


if __name__ == "__main__":
    generate()
