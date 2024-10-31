import qrcode
from PIL import Image, ImageDraw

## Define the error correction levels
ERROR_CORRECTION_LEVELS= {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H
}

def generate_custom_qr(data, output_file, fill_color="black", back_color="white", gradient=False, gradient_rotation=0, rounded=False, borderless=False, error_correction="L"):
    correction_level = ERROR_CORRECTION_LEVELS.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_L)

    ## Generate QR code with selected error correction level and border
    border_size = 0 if borderless else 4
    qr = qrcode.QRCode(
        version=1,
        error_correction=correction_level,
        box_size=10,
        border=border_size,
    )
    qr.add_data(data)
    qr.make(fit=True)

    ## Create the QR Code image
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGBA')

    ## Apply gradient if selected
    if gradient:
        gradient_img = Image.new("RGBA", img.size)
        draw = ImageDraw.Draw(gradient_img)
        for y in range(gradient_img.height):
            color_value = int(255 * (y / gradient_img.height))
            color = (color_value, color_value, color_value, 255) if gradient_rotation % 180 == 0 else (color_value, 255)
            draw.line([(0, y), (gradient_img.width, y)], fill=color)
        img = Image.alpha_composite(img, gradient_img)
    ## Apply Rounded corners if selected
    if rounded:
        rounded_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=20, fill=255)
        rounded_img.paste(img, (0, 0), mask=mask)
        img = rounded_img

    img.save(output_file)
    print(f"QR code saved to {output_file}")

if __name__ == "__main__":
    data = input("Enter the data for the QR code: ")
    output_file = input("Enter the output filename to save the QR code (e.g., qrcode.png): ")
    fill_color = input("Enter the fill color for the QR code: ")
    back_color = input("Enter the background color for the QR code: ")
    gradient = input("Apply gradient? (yes/no): ").strip().lower() == "yes"
    gradient_rotation = int(input("Enter gradient rotation (0 for vertical, 90 for horizontal): ")) if gradient else 0
    rounded = input("Use rounded corners? (yes/no): ").strip().lower() == "yes"
    borderless = input("Generate borderless QR? (yes/no): ").strip().lower() == "yes"
    error_correction = input("Choosee error correction level (L, M, Q, H): ").upper()

    generate_custom_qr(data, output_file, fill_color, back_color, gradient, gradient_rotation, rounded, borderless, error_correction)
