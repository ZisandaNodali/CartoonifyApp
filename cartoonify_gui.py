import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import Label, Button
import cv2
from PIL import Image, ImageTk
import numpy as np

class CartoonifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartoonify Image App")
        self.root.geometry("800x600")
        self.root.configure(bg='white')

        self.original_image = None
        self.cartoon_image = None

        # Buttons
        self.open_button = Button(root, text="Open Image", command=self.open_image, bg="#4CAF50", fg="white")
        self.open_button.pack(pady=10)

        self.cartoonify_button = Button(root, text="Cartoonify", command=self.cartoonify_image, state='disabled', bg="#2196F3", fg="white")
        self.cartoonify_button.pack(pady=10)
        self.sketch_button = Button(root, text="Sketch Filter", command=self.sketch_filter, state='disabled', bg="#9C27B0", fg="white")
        self.sketch_button.pack(pady=10)

        self.oil_button = Button(root, text="Oil Paint Filter", command=self.oil_paint_filter, state='disabled', bg="#FF9800", fg="white")
        self.oil_button.pack(pady=10)


        self.save_button = Button(root, text="Save Image", command=self.save_image, state='disabled', bg="#f44336", fg="white")
        self.save_button.pack(pady=10)
        self.reset_button = Button(root, text="Reset", command=self.reset_app, bg="#9E9E9E", fg="white")
        self.reset_button.pack(pady=10)

        # Image Label
        # Image display frame (side-by-side)
        self.image_frame = tk.Frame(root, bg="white")
        self.image_frame.pack(pady=20)

        # Labels
        self.original_label = Label(self.image_frame, text="Original Image", bg="white")
        self.original_label.grid(row=0, column=0, padx=20)

        self.cartoon_label = Label(self.image_frame, text="Cartoonified Image", bg="white")
        self.cartoon_label.grid(row=0, column=1, padx=20)

        self.panel_original = Label(self.image_frame, bg="white")
        self.panel_original.grid(row=1, column=0, padx=20)

        self.panel_cartoon = Label(self.image_frame, bg="white")
        self.panel_cartoon.grid(row=1, column=1, padx=20)

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = cv2.imread(file_path)
            self.original_image = image
            self.show_image(image, is_original=True)
            self.cartoonify_button.config(state='normal')
            self.sketch_button.config(state='normal')
            self.oil_button.config(state='normal')



    def show_image(self, cv_img, is_original=True):
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_resized = img_pil.resize((350, 350))
        img_tk = ImageTk.PhotoImage(img_resized)

        if is_original:
            self.panel_original.configure(image=img_tk)
            self.panel_original.image = img_tk
        else:
            self.panel_cartoon.configure(image=img_tk)
            self.panel_cartoon.image = img_tk


    def cartoonify_image(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        img = self.original_image
        img = cv2.resize(img, (600, 600))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray_blur, 255,
                              cv2.ADAPTIVE_THRESH_MEAN_C,
                              cv2.THRESH_BINARY, blockSize=block_size, C=c_value)
        color = cv2.bilateralFilter(img, d=9, sigmaColor=250, sigmaSpace=250)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        block_size = self.block_size_slider.get()
        if block_size % 2 == 0:  # Make sure it's odd
            block_size += 1

        c_value = self.c_slider.get()

        self.cartoon_image = cartoon
        self.show_image(cartoon, is_original=False)
        self.save_button.config(state='normal')

    def sketch_filter(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        inv = 255 - img
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(img, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

        self.cartoon_image = sketch_bgr
        self.show_image(sketch_bgr, is_original=False)
        self.save_button.config(state='normal')

    def oil_paint_filter(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        # Convert to LAB for stylized filtering
        img = cv2.edgePreservingFilter(self.original_image, flags=2, sigma_s=60, sigma_r=0.4)
        self.cartoon_image = img
        self.show_image(img, is_original=False)
        self.save_button.config(state='normal')


    def save_image(self):
        if self.cartoon_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.cartoon_image)
                messagebox.showinfo("Saved", "Image saved successfully!")
    
    def reset_app(self):
        self.original_image = None
        self.cartoon_image = None

        # Clear image display
        self.image_label.config(image=None)
        self.image_label.image = None  # Remove image reference to clear from memory

        # Disable buttons
        self.cartoonify_button.config(state='disabled')
        self.save_button.config(state='disabled')



if __name__ == "__main__":
    root = tk.Tk()
    app = CartoonifyApp(root)
    root.mainloop()
