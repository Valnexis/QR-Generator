import qrcode
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, PngImagePlugin
import argparse

## Basic QR code generator function placeholder

def generate_qr_code(data, fill_color="black", back_color="white", error_correction="L", logo_path=None):
    ## Temp function
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGBA')

    ## Embed logo if provided
    if logo_path:
        try:
            logo = Image.open(logo_path)
            logo.thumbnail((img.size[0] // 5, img.size[1] // 5))
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, logo)
        except Exception as e:
            messagebox.showerror("Logo Error", f"Couldn't add logo: {e}")

    return img

## GUI Function
def qr_gui():
    ## Setup main window
    root = tk.Tk()
    root.title("QR Code Generator")
    root.geometry("400x500")

    ## Input for data
    tk.Label(root, text="Data for QR Code:").pack(pady=5)
    data_entry = tk.Entry(root, width=50)
    data_entry.pack(pady=5)

    ## Color picker for fill color
    def pick_fill_color():
        color = colorchooser.askcolor(title="Choose fill color")[1]
        if color:
            fill_color_btn.config(bg=color)
            fill_color_btn.color = color
    tk.Label(root, text="Fill Color:").pack(pady=5)
    fill_color_btn = tk.Button(root, text="Fill Color", command=pick_fill_color)
    fill_color_btn.color = "black" ## Default color
    fill_color_btn.pack(pady=5)

    ## Color picker for background color
    def pick_back_color():
        color = colorchooser.askcolor(title="Choose background color")[1]
        if color:
            back_color_btn.config(bg=color)
            back_color_btn.color = color

    tk.Label(root, text="Background Color:").pack(pady=5)
    back_color_btn = tk.Button(root, text="Pick Color", command=pick_back_color)
    back_color_btn.color = "white" ## Default
    back_color_btn.pack(pady=5)

    ## Dropdown for Error Correction Level
    tk.Label(root, text="Error Correction Level:").pack(pady=5)
    error_correction = tk.StringVar(value="L")
    correction_menu = tk.OptionMenu(root, error_correction, "L", "M", "Q", "H")
    correction_menu.pack(pady=5)

    ## Logo upload
    logo_path = tk.StringVar()
    def select_logo():
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if path:
            logo_path.set(path)

    tk.Label(root, text="Logo (optional):").pack(pady=5)
    logo_button = tk.Button(root, text="Select Logo", command=select_logo)
    logo_button.pack(pady=5)

    ## Generate button and display output
    def generate_and_show():
        data = data_entry.get()
        if not data:
            messagebox.showerror("Input Error", "Please enter data for the QR code.")
            return
        fill_color = fill_color_btn.color
        back_color = back_color_btn.color
        error_level = error_correction.get()
        logo = logo_path.get() if logo_path.get() else None

        ## Generate QR code with parameters
        img = generate_qr_code(data, fill_color, back_color, error_level, logo)

        ## Display the image in a new window
        display_window = tk.Toplevel(root)
        display_window.title("Generated QR Code")
        display_window.geometry("300x300")

        img_tk = ImageTk.PhotoImage(img.resize((250, 250)))
        img_label = tk.Label(display_window, image=img_tk)
        img_label.image = img_tk
        img_label.pack()

        ## Save button in display window
        def save_image():
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if save_path:
                img.save(save_path)
                messagebox.showinfo("Saved QR Code", f"Image saved to {save_path}.")

        save_btn = tk.Button(display_window, text="Save Image", command=save_image)
        save_btn.pack(pady=5)

    generate_btn = tk.Button(root, text="Generate QR Code", command=generate_and_show)
    generate_btn.pack(pady=20)

    root.mainloop()

## Run the GUI
if __name__ == "__main__":
    qr_gui()