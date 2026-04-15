#!/usr/bin/env python3
"""
App Store / Google Play Screenshot Composer
Composites headline text, device frame template, and app screenshot
into a pixel-perfect image at the correct store dimensions.

Supported platforms:
  --platform ios     → 1290×2796 (iPhone 6.7", App Store Connect default)
  --platform android → 1080×1920 (Google Play phone)
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

FONT_PATH = "/Library/Fonts/SF-Pro-Display-Black.otf"

# ── Platform configs ─────────────────────────────────────────────────
CONFIGS = {
    "ios": {
        "canvas_w": 1290,
        "canvas_h": 2796,
        "device_w": 1030,
        "bezel": 15,
        "screen_corner_r": 62,
        "device_y": 720,
        "text_top": 200,
        "verb_size_max": 256,
        "verb_size_min": 150,
        "desc_size": 124,
        "verb_desc_gap": 20,
        "desc_line_gap": 24,
        "frame_file": "device_frame.png",
    },
    "android": {
        "canvas_w": 1080,
        "canvas_h": 1920,
        "device_w": 860,
        "bezel": 12,
        "screen_corner_r": 40,
        "device_y": 490,
        "text_top": 130,
        "verb_size_max": 200,
        "verb_size_min": 110,
        "desc_size": 90,
        "verb_desc_gap": 16,
        "desc_line_gap": 18,
        "frame_file": "android_device_frame.png",
    },
}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def word_wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, max_w, size_max, size_min):
    """Return the largest font size where text fits within max_w."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        font = ImageFont.truetype(FONT_PATH, size)
        bbox = dummy.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return font
    return ImageFont.truetype(FONT_PATH, size_min)


def draw_centered(draw, y, text, font, canvas_w, line_gap, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text((canvas_w // 2, y - bbox[1]), line, fill="white", font=font, anchor="mt")
        y += h + line_gap
    return y


def compose(bg_hex, verb, desc, screenshot_path, output_path, platform="ios"):
    cfg = CONFIGS[platform]

    canvas_w = cfg["canvas_w"]
    canvas_h = cfg["canvas_h"]
    device_w = cfg["device_w"]
    bezel = cfg["bezel"]
    screen_w = device_w - 2 * bezel
    screen_corner_r = cfg["screen_corner_r"]
    device_y = cfg["device_y"]
    text_top = cfg["text_top"]
    verb_size_max = cfg["verb_size_max"]
    verb_size_min = cfg["verb_size_min"]
    desc_size = cfg["desc_size"]
    verb_desc_gap = cfg["verb_desc_gap"]
    desc_line_gap = cfg["desc_line_gap"]
    max_text_w = int(canvas_w * 0.92)
    max_verb_w = int(canvas_w * 0.92)

    frame_path = os.path.join(os.path.dirname(__file__), "assets", cfg["frame_file"])

    bg = hex_to_rgb(bg_hex)

    # ── 1. Canvas ───────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*bg, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 2. Fonts ────────────────────────────────────────────────────
    verb_font = fit_font(verb.upper(), max_verb_w, verb_size_max, verb_size_min)
    desc_font = ImageFont.truetype(FONT_PATH, desc_size)

    # ── 3. Draw headline text ────────────────────────────────────────
    y = text_top
    y = draw_centered(draw, y, verb.upper(), verb_font, canvas_w, desc_line_gap)
    y += verb_desc_gap
    draw_centered(draw, y, desc.upper(), desc_font, canvas_w, desc_line_gap, max_w=max_text_w)

    # ── 4. Screenshot into screen area ──────────────────────────────
    device_x = (canvas_w - device_w) // 2
    screen_x = device_x + bezel
    screen_y = device_y + bezel

    shot = Image.open(screenshot_path).convert("RGBA")

    scale = screen_w / shot.width
    sc_w = screen_w
    sc_h = int(shot.height * scale)
    shot = shot.resize((sc_w, sc_h), Image.LANCZOS)

    screen_h = canvas_h - screen_y + 500

    scr_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=255,
    )

    scr_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(scr_layer).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=(0, 0, 0, 255),
    )
    scr_layer.paste(shot, (screen_x, screen_y))
    scr_layer.putalpha(scr_mask)

    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 5. Device frame template ─────────────────────────────────────
    frame_template = Image.open(frame_path).convert("RGBA")

    frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    frame_layer.paste(frame_template, (device_x, device_y))
    canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 6. Save ──────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"Done: {output_path} ({canvas_w}x{canvas_h}, platform={platform})")


def main():
    p = argparse.ArgumentParser(description="Compose App Store / Google Play screenshot")
    p.add_argument("--bg", required=True, help="Background hex colour (#E31837)")
    p.add_argument("--verb", required=True, help="Action verb (TRACK)")
    p.add_argument("--desc", required=True, help="Benefit descriptor (TRADING CARD PRICES)")
    p.add_argument("--screenshot", required=True, help="Simulator/emulator screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument(
        "--platform",
        choices=["ios", "android"],
        default="ios",
        help="Target platform (default: ios)",
    )
    args = p.parse_args()

    compose(args.bg, args.verb, args.desc, args.screenshot, args.output, args.platform)


if __name__ == "__main__":
    main()
