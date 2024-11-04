import qrcode
from PIL import Image, ImageDraw
import argparse

## Define the error correction levels
ERROR_CORRECTION_LEVELS= {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H
}

def determine_box_size(data_length):
    ## Determine box size dynamically based on data length.
    if data_length < 50:
        return 10
    elif data_length < 100:
        return 8
    elif data_length < 200:
        return 6
    else:
        return 4

def determine_version(data_length):
    ## Determine QR version dynamically based on data length.
    if data_length < 50:
        return 1
    elif data_length < 100:
        return 5
    elif data_length < 200:
        return 10
    else:
        return 15
def generate_qr(data, output_file, fill_color="black", back_color="white", gradient=False, gradient_rotation=0, rounded=False, borderless=False, error_correction="L", extension="png", logo_path=None):
    data_length = len(data)
    box_size = determine_box_size(data_length)
    version = determine_version(data_length)
    correction_level = ERROR_CORRECTION_LEVELS.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_L)
    border_size = 0 if borderless else 4

    qr = qrcode.QRCode(
        version=version,
        error_correction=correction_level,
        box_size=box_size,
        border=border_size,
    )
    qr.add_data(data)
    qr.make(fit=True)

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

    ## Embed logo if provided
    if logo_path:
        try:
            logo = Image.open(logo_path).convert('RGBA')
            ## Calculate the maximum size for the logo
            max_logo_size = (img.size[0] // 5, img.size[1] // 5)
            logo.thumbnail(max_logo_size, Image.ANTIALIAS)
            ## Calculate position for centering the logo
            logo_position = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, logo_position, mask=logo)
        except FileNotFoundError:
            print("Logo file not found. Please check the path and try again.")

    ## Save image in specified format
    img.save(f"{output_file}.{extension}", format=extension.upper())
    print(f"QR code saved as {output_file}.{extension}")

def batch_generate_qr(data_list, output_prefix="qr", fill_color="black", back_color="white", gradient=False, gradient_rotation=0, rounded=False, borderless=False, error_correction="L", extension="png", logo_path=None):
    for i, data in enumerate(data_list, start=1):
        output_file = f"{output_prefix}_{i}"
        generate_qr(data, output_file, fill_color, back_color, gradient, gradient_rotation, rounded, borderless, error_correction, extension, logo_path)

def main():
    parser = argparse.ArgumentParser(description="Generate QR code from given data")
    parser.add_argument("mode", choices=["single", "batch"], help="Choose mode: 'single' or 'batch'")
    parser.add_argument("--data", help="Data for single QR code (required for single mode)")
    parser.add_argument("--file", help="File containing data for batch QR generation (one entry per line, required for batch mode)")
    parser.add_argument("--output-prefix", default="qr_code", help="Prefix for output filenames")
    parser.add_argument("--fill-color", default="black", help="Color of the QR")
    parser.add_argument("--back-color", default="white", help="Color of the background")
    parser.add_argument("--gradient", action="store_true", help="Generate gradient QR")
    parser.add_argument("--gradient-rotation", default=0, type=int, choices=[0, 90], help="Rotation of the gradient QR")
    parser.add_argument("--rounded", action="store_true", help="Generate rounded QR")
    parser.add_argument("--borderless", action="store_true", help="Generate borderless QR")
    parser.add_argument("--error-correction", choices=["L", "M", "Q", "H"], default="L", help="Error correction level")
    parser.add_argument("--extension", default="png", choices=["png", "jpg", "bmp", "tiff", "jpeg"], help="File extension for output files")
    parser.add_argument("--logo", help="Path to logo file")

    args = parser.parse_args()

    if args.mode == "single":
        if not args.data:
            parser.error("The --data argument is required for single mode.")
        output_file = args.output_prefix
        generate_qr(args.data, output_file, args.fill_color, args.back_color, args.gradient, args.gradient_rotation, args.rounded, args.borderless, args.error_correction, args.extension, args.logo)

    elif args.mode == "batch":
        if not args.file:
            parser.error("The --file argument is required for batch mode.")
        try:
            with open(args.file, "r") as file:
                data_list = [line.strip() for line in file if line.strip()]
            batch_generate_qr(data_list, args.output_prefix, args.fill_color, args.back_color, args.gradient, args.gradient_rotation, args.rounded, args.borderless, args.error_correction, args.extension, args.logo)
        except FileNotFoundError:
            print("File not found. Please check the path and try again.")

if __name__ == "__main__":
    main()
