import qrcode
from PIL import Image, ImageDraw
import os
import argparse
from urllib.parse import urlparse

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def generate_qr(link, qr_color, background_color, icon_path, output_folder, output_name, border_size):
    if not validate_url(link):
        print("Invalid URL. Please provide a valid link.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=border_size
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color=qr_color, back_color=background_color).convert('RGB')

    if icon_path:
        try:
            icon = Image.open(icon_path)
            img_w, img_h = img.size
            icon_size = int(min(img_w, img_h) / 4)
            icon = icon.resize((icon_size, icon_size), Image.ANTIALIAS)

            pos = ((img_w - icon_size) // 2, (img_h - icon_size) // 2)
            img.paste(icon, pos, mask=icon if icon.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Error loading icon: {e}")

    output_path = os.path.join(output_folder, f'{output_name}.png')
    img.save(output_path)
    print(f"QR saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a custom QR code.")
    parser.add_argument('link', help="The URL or text for the QR code.")
    parser.add_argument('--qr-color', default="black", help="QR code color (default is black).")
    parser.add_argument('--bg-color', default="white", help="Background color (default is white).")
    parser.add_argument('--icon', default=None, help="Path to an optional icon image to place in the center.")
    parser.add_argument('--output-folder', default=os.getcwd(), help="Output folder (default is current directory).")
    parser.add_argument('--output-name', default="generated_qr", help="Output file name (default is 'generated_qr').")
    parser.add_argument('--border', type=int, default=4, help="Border size (default is 4).")

    args = parser.parse_args()

    generate_qr(args.link, args.qr_color, args.bg_color, args.icon, args.output_folder, args.output_name, args.border)

if __name__ == "__main__":
    main()