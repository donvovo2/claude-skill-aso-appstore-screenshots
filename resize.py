#!/usr/bin/env python3
"""
resize.py — Cross-platform App Store screenshot crop/resize.
Crops to the correct aspect ratio (centre horizontally, top preserved)
then resizes to exact App Store Connect pixel dimensions.

Requires: pip install Pillow
"""

import argparse
import sys
from PIL import Image


def crop_and_resize(input_path, output_path, target_w, target_h):
    img = Image.open(input_path)
    actual_w, actual_h = img.size

    crop_w = round(actual_h * target_w / target_h)
    offset_x = round((actual_w - crop_w) / 2)

    if crop_w > actual_w:
        print(f"ERROR: Image is too narrow to crop to {target_w}x{target_h}.")
        print(f"  Input size: {actual_w}x{actual_h}, required crop width: {crop_w}")
        sys.exit(1)

    cropped = img.crop((offset_x, 0, offset_x + crop_w, actual_h))
    resized = cropped.resize((target_w, target_h), Image.LANCZOS)
    resized.save(output_path, "JPEG", quality=95)

    final_w, final_h = resized.size
    print(f"{output_path}: {final_w}x{final_h}")


def main():
    parser = argparse.ArgumentParser(
        description="Crop and resize an image to exact App Store Connect dimensions."
    )
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output", required=True, help="Output image path")
    parser.add_argument("--width", type=int, default=1290, help="Target width (default: 1290)")
    parser.add_argument("--height", type=int, default=2796, help="Target height (default: 2796)")
    args = parser.parse_args()

    crop_and_resize(args.input, args.output, args.width, args.height)


if __name__ == "__main__":
    main()
