import qrcode

def generate_qr(data, output_file):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(output_file)
    print(f"QR code saved to {output_file}")

if __name__ == "__main__":
    data = input("Enter the data for the QR code: ")
    output_file = input("Enter the output filename to save the QR code (e.g., qrcode.png): ")
    generate_qr(data, output_file)
