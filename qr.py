import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageSequence, ImageColor
import os
import argparse
from urllib.parse import urlparse
import re
from tqdm import tqdm
import csv
import logging
import numpy as np
import logging
from concurrent.futures import ThreadPoolExecutor

## Setup logging for error logging
logging.basicConfig(filename='qr_errors.log', level=logging.ERROR)

## URL Validation
def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        logging.error(f"Invalid URL: {url}")
        return False

## Validate hex color codes
def is_valid_color(color):
    try:
        Image.new('RGB', (1,1), color)
        return True
    except ValueError:
        pass
    hex_pattern = r'^#[0-9A-Fa-f]{6}'
    if re.match(hex_pattern, color):
        return True
    logging.error(f"Invalid color: {color}")
    return False

## Progress Bar
def progress_bar(iterable, total, description):
    return tqdm(iterable, total=total, desc=description)

## Gradient Fill
def hex_to_rgb(hex_color):
    return ImageColor.getrgb(hex_color)

def apply_gradient(img, color1, color2):
    img_w, img_h = img.size

    if isinstance(color1, str):
        color1 = hex_to_rgb(color1)
    if isinstance(color2, str):
        color2 = hex_to_rgb(color2)

    gradient = Image.new('RGB', (img_w, img_h), color1)

    for y in range(img_h):
        r = int((color2[0] - color1[0]) * (y / img_h) + color1[0])
        g = int((color2[1] - color1[1]) * (y / img_h) + color1[1])
        b = int((color2[2] - color1[2]) * (y / img_h) + color1[2])

        for x in range(img_w):
            gradient.putpixel((x, y), (r, g, b))

    blended_img = Image.blend(img, gradient, alpha=0.5)
    return blended_img

## Animated QR
def generate_animated_qr(link, colors, frames=10, duration=100, output_path='animated_qr.gif'):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image().convert("RGB")

    frames_list = []
    for color in colors:
        img_colored = qr.make_image(fill_color=color, back_color="white").convert("RGB")
        img_colored = img_colored.resize(img.size)
        frames_list.append(img_colored)

    img_colored.save(output_path, save_all=True, append_images=frames_list, loop=0, duration=duration)
    print(f"Animateed QR code saved to {output_path}")

## QR Generator
def generate_qr(link, qr_color, background_color, icon_path, output_folder, output_name, border_size, version, error_correction, icon_position, output_format, icon_opacity, label_text=None, size=None, gradient=None, borderless=False, metadata=None, dark_mode=False, grid_size=None):
    if not validate_url(link):
        print("Invalid URL. Please provide a valid link.")
        return

## Validate Colors
    if not is_valid_color(qr_color):
        print(f"Invalid QR color: {qr_color}. Using default.")
        qr_color="black"
    if not is_valid_color(background_color):
        print(f"Invalid background color: {background_color}. Using default.")
        background_color="white"

    if dark_mode:
        qr_color = "white"
        background_color = "black"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

## Error Correction Levels
    error_correction_levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }

    if error_correction not in error_correction_levels:
        logging.error(f"Invalid error correction level: {error_correction}")
        error_correction = 'H'

    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction_levels[error_correction],
        box_size=10 if not size else int(size[0] / 30),
        border=0 if borderless else border_size
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color=qr_color, back_color=background_color).convert('RGB')

    if gradient:
        img = apply_gradient(img, gradient[0], gradient[1])

    if icon_path:
        try:
            icon = Image.open(icon_path)
            img_w, img_h = img.size
            icon_size = int(min(img_w, img_h) / 4)
            icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)

            if icon_opacity < 1.0:
                icon = icon.convert("RGBA")
                alpha = icon.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(icon_opacity)
                icon.putalpha(alpha)

            positions = {
                "center": ((img_w - icon_size) // 2, (img_h - icon_size) // 2),
                "top-left": (img_w // 10, img_h // 10),
                "bottom-right": (img_w - icon_size - img_w // 10, img_h - icon_size - img_h // 10)
            }
            pos = positions.get(icon_position, positions["center"])

            img.paste(icon, pos, mask=icon if icon.mode == 'RGBA' else None)
        except Exception as e:
            logging.error(f"Error loading icon: {e}")

    if label_text:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        label_position = ((img_w - text_w) // 2, img_h - text_h - 10)
        draw.text(label_position, label_text, fill="black", font=font)

## Resize
    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)

## Save Metadata
    if metadata:
        metadata_file = os.path.join(output_folder, f"{output_name}_metadata.txt")
        with open(metadata_file, "w") as f:
            f.write(f"URL: {link}\nMetadata: {metadata}")

    output_path = os.path.join(output_folder, f'{output_name}.{output_format}')
    img.save(output_path)
    print(f"QR saved to {output_path}")

## Batch QR Generation
def batch_generate_qr(input_file, **kwargs):
    ext = os.path.splitext(input_file)[1].lower()
    links = []

    if ext == ".csv":
        try:
            with open(input_file, newline='') as csvfile:
                reader = csv.reader(csvfile)
                links = [row[0] for row in reader if validate_url(row[0])]
        except FileNotFoundError as e:
            logging.error(f"File not found: {input_file}")
    else:
        try:
            with open(input_file, 'r') as f:
                links = [line.strip() for line in f if validate_url(line.strip())]
        except FileNotFoundError as e:
            logging.error(f"File not found: {input_file}")

    for idx, link in enumerate(progress_bar(links, total=len(links), description="Generating QR codes")):
        kwargs['output_name'] = f"{kwargs['output_name']}_{idx+1}"
        generate_qr(link, **kwargs)

## Main Function
def main():
    parser = argparse.ArgumentParser(description="Generate a custom QR code.")
    parser.add_argument('link', help="The URL or text for the QR code. The URL must have transfer protocol (http(s)://) Can be a file for batch generation")
    parser.add_argument('--qr-color', default="black", help="QR code color (default is black).")
    parser.add_argument('--background-color', default="white", help="Background color (default is white).")
## Icon Related Arguments
    parser.add_argument('--icon-path', default=None, help="Path to an optional icon image to place in the center.")
    parser.add_argument('--icon-position', default="center", choices=["center", "top-left", "bottom-right"], help="Position of the icon (default is center).")
    parser.add_argument('--icon-opacity', type=float, default=1.0, help="Opacity of the icon (0.0 to 1.0, default is 1.0).")
## Folder and File Output
    parser.add_argument('--output-folder', default=".", help="Output folder (default is current directory).")
    parser.add_argument('--output-name', default="generated_qr", help="Output file name (default is 'generated_qr').")
    parser.add_argument('--output-format', default="png", choices=["png", "jpeg", "jpg"], help="Output file format (default is png).")
    parser.add_argument('--border-size', type=int, default=4, help="Border size (default is 4).")
    parser.add_argument('--version', type=int, default=1, help="QR code version (default is 1, range 1-40).")
    parser.add_argument('--error-correction', default='H', choices=["L", "M", "Q", "H"], help="Error correction level (default is H).")
## Advanced Features
    parser.add_argument('--label-text', default=None, help="Optional text label below the QR code.")
    parser.add_argument('--size', nargs=2, type=int, help="Custom size for the QR code in pixels (width height).")
    parser.add_argument('--gradient', nargs=2, help="Gradient colors for the QR code (start_color end_color).")
    parser.add_argument('--borderless', action='store_true', help="Generate QR code without a border.")
    parser.add_argument('--metadata', help="Optional metadata to embed in the QR code.")
    parser.add_argument('--dark-mode', action='store_true', help="Enable dark mode by switching to white QR and black background.")

    args = parser.parse_args()

## Argument Handling for Gradient Colors
    if args.gradient:
        args.gradient = [hex_to_rgb(args.gradient[0]), hex_to_rgb(args.gradient[1])]

## Handling Single or Batch QR Generation
    if os.path.isfile(args.link):
        batch_generate_qr(args.link, **vars(args))
    else:
        kwargs = vars(args).copy()
        link = kwargs.pop('link')
        if validate_url(link):
            generate_qr(link, **kwargs)
        else:
            print("Invaild input. Provide a valid URL or a file path.")

if __name__ == "__main__":
    main()