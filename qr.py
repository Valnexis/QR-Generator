import qrcode
from PIL import Image, ImageDraw
import os

def generate_qr():
    link = input("Enter the link:")

    qr_color = input("Enter the QR color (default is black):") or "black"
    background_color = input("Enter the QR background color (default is white):") or "white"

    icon_path = input("Enter path to the icon (optional, leave blank if none): ").strip()
    output_folder = input("Enter output folder (default is current directory): ").strip() or os.getcwd()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
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

    output_path = os.path.join(output_folder, "qr.png")
    img.save(output_path)
    print(f"QR saved to {output_path}")

if __name__ == "__main__":
    generate_qr()