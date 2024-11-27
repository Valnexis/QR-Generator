import argparse
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

# Error correction levels mapping
ERROR_CORRECTION_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H
}


# Function to generate QR code
def generate_qr_code(data, fill_color="black", back_color="white", error_correction="L", logo_path=None, size=300):
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECTION_MAP.get(error_correction, ERROR_CORRECT_L)
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")

    # Add logo if provided
    if logo_path:
        try:
            logo = Image.open(logo_path)
            logo.thumbnail((size // 5, size // 5))
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, logo)
        except Exception as e:
            raise ValueError(f"Could not add logo: {e}")

    return img.resize((size, size))


# GUI implementation
def run_gui():
    def update_preview():
        try:
            data = data_entry.get()
            if not data:
                raise ValueError("Data cannot be empty.")
            fill_color = fill_color_btn.color
            back_color = back_color_btn.color
            error_level = error_correction.get()
            logo = logo_path.get() if logo_path.get() else None
            size = int(size_slider.get())

            # Generate preview
            img = generate_qr_code(data, fill_color, back_color, error_level, logo, size)
            img_tk = ImageTk.PhotoImage(img)
            qr_preview_label.config(image=img_tk)
            qr_preview_label.image = img_tk  # Keep a reference
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_and_save():
        try:
            data = data_entry.get()
            if not data:
                raise ValueError("Data cannot be empty.")
            fill_color = fill_color_btn.color
            back_color = back_color_btn.color
            error_level = error_correction.get()
            logo = logo_path.get() if logo_path.get() else None
            size = int(size_slider.get())

            # Generate QR code
            img = generate_qr_code(data, fill_color, back_color, error_level, logo, size)

            # Save file dialog
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp")]
            )
            if save_path:
                img.save(save_path)
                messagebox.showinfo("Success", f"QR Code saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Main GUI window
    root = tk.Tk()
    root.title("QR Code Generator")
    root.geometry("500x600")

    # Data input
    tk.Label(root, text="Data for QR Code:").pack(pady=5)
    data_entry = tk.Entry(root, width=50)
    data_entry.pack(pady=5)

    # Fill color
    def pick_fill_color():
        color = colorchooser.askcolor(title="Choose Fill Color")[1]
        if color:
            fill_color_btn.config(bg=color)
            fill_color_btn.color = color

    tk.Label(root, text="Fill Color:").pack(pady=5)
    fill_color_btn = tk.Button(root, text="Pick Color", command=pick_fill_color)
    fill_color_btn.color = "black"
    fill_color_btn.pack(pady=5)

    # Background color
    def pick_back_color():
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            back_color_btn.config(bg=color)
            back_color_btn.color = color

    tk.Label(root, text="Background Color:").pack(pady=5)
    back_color_btn = tk.Button(root, text="Pick Color", command=pick_back_color)
    back_color_btn.color = "white"
    back_color_btn.pack(pady=5)

    # Error correction level
    tk.Label(root, text="Error Correction Level:").pack(pady=5)
    error_correction = tk.StringVar(value="L")
    correction_menu = tk.OptionMenu(root, error_correction, "L", "M", "Q", "H")
    correction_menu.pack(pady=5)

    # Logo selection
    logo_path = tk.StringVar()

    def select_logo():
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if path:
            logo_path.set(path)

    tk.Label(root, text="Logo (optional):").pack(pady=5)
    logo_button = tk.Button(root, text="Select Logo", command=select_logo)
    logo_button.pack(pady=5)

    # QR size
    tk.Label(root, text="QR Code Size:").pack(pady=5)
    size_slider = tk.Scale(root, from_=100, to=1000, orient="horizontal")
    size_slider.set(300)
    size_slider.pack(pady=5)

    # QR Preview
    tk.Label(root, text="QR Code Preview:").pack(pady=5)
    qr_preview_label = tk.Label(root)
    qr_preview_label.pack(pady=10)

    # Update preview on any change
    preview_btn = tk.Button(root, text="Update Preview", command=update_preview)
    preview_btn.pack(pady=5)

    # Generate and save
    generate_btn = tk.Button(root, text="Generate & Save QR Code", command=generate_and_save)
    generate_btn.pack(pady=20)

    root.mainloop()


# CLI implementation
def run_cli():
    parser = argparse.ArgumentParser(description="QR Code Generator CLI")
    # Define CLI arguments here (similar to the previous CLI implementation)
    args = parser.parse_args()
    # Implement CLI logic here (reuse the same functions)


# Main entry point
if __name__ == "__main__":
    import sys

    if "--gui" in sys.argv:
        run_gui()
    else:
        run_cli()
