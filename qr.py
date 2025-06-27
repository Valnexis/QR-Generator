import qrcode
from qrcode.console_scripts import error_correction

data = input("Enter the data to encode: ")

version = int(input("Select the QR version between 1-40: "))
if version < 1 or version > 40:
    print("Invalid QR version. Defaulting to 40.")
    version = 40


error_correction = input("Enter error correction level (L-M-H-Q). Default is Q: ")
if error_correction == "L":
    error_correction = qrcode.constants.ERROR_CORRECT_L
elif error_correction == "M":
    error_correction = qrcode.constants.ERROR_CORRECT_M
elif error_correction == "H":
    error_correction = qrcode.constants.ERROR_CORRECT_H
elif error_correction == "Q":
    error_correction = qrcode.constants.ERROR_CORRECT_Q
else:
    print("Invalid error correction level. Defaulting to Q")
    error_correction = qrcode.constants.ERROR_CORRECT_Q

box_size = int(input("Enter box size: "))
border = int(input("Enter the border size: "))
fill_color = input("Enter fill color: ")
back_color = input("Enter background color: ")

name = input("Filename to save: ")

qr = qrcode.QRCode(
    version=version,
    error_correction=error_correction,
    box_size=box_size,
    border=border
)

qr.add_data(data)
qr.make()

img = qr.make_image(fill_color=fill_color, back_color=back_color)
img.save(f"{name}.png")