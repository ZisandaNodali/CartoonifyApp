import tkinter as tk
from tkinter import Button, Label, filedialog, messagebox, Frame, Toplevel
import cv2
from PIL import Image, ImageTk, ImageDraw
import os
import time

class SplashScreen:
    def __init__(self, parent):
        # Create a toplevel window
        self.splash = Toplevel(parent)
        self.splash.title("Cartoonify")
        self.splash.geometry("400x400")
        
        # Remove window decorations for a cleaner look
        self.splash.overrideredirect(True)
        
        # Center on screen
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 400) // 2
        self.splash.geometry(f"400x400+{x}+{y}")
        
        # Configure background
        self.splash.configure(bg="#001839")
        
        # Create a frame for content
        content_frame = Frame(self.splash, bg="#001839")
        content_frame.pack(expand=True, fill="both")
        
        # Try to load and display the logo
        try:
            logo_img = Image.open("images\\logo.png")
            # Resize if needed
            logo_img = logo_img.resize((300, 300), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            
            logo_label = Label(content_frame, image=logo_photo, bg="#001839")
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(pady=(50, 20))
        except Exception as e:
            print(f"Error loading logo: {e}")
            # If logo can't be loaded, display text instead
            logo_label = Label(content_frame, text="Cartoonify", font=("Arial", 30, "bold"), 
                              bg="#001839", fg="white")
            logo_label.pack(pady=(80, 20))
        
        # Loading indicator
        loading_label = Label(content_frame, text="Loading...", font=("Arial", 12), 
                             bg="#001839", fg="#AAAAAA")
        loading_label.pack(pady=20)
    
    def destroy(self):
        self.splash.destroy()

class CameraWindow:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        # Create camera window
        self.window = Toplevel(parent)
        self.window.title("Camera")
        self.window.geometry("680x520")
        self.window.configure(bg="#001839")
        
        # Center on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 680) // 2
        y = (screen_height - 520) // 2
        self.window.geometry(f"680x520+{x}+{y}")
        
        # Add a title
        title_label = Label(self.window, text="Camera Preview", font=("Arial", 16), bg="#001839", fg="white")
        title_label.pack(pady=10)
        
        # Camera preview frame
        self.camera_frame = Label(self.window, bg="black", width=640, height=480)
        self.camera_frame.pack(pady=10)
        
        # Buttons frame
        buttons_frame = Frame(self.window, bg="#001839")
        buttons_frame.pack(pady=10)
        
        # Capture button
        self.capture_button = Button(buttons_frame, text="Capture", command=self.capture_image,
                                    bg="#1976D2", fg="white", font=("Arial", 12),
                                    padx=15, pady=5, borderwidth=0)
        self.capture_button.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        self.cancel_button = Button(buttons_frame, text="Cancel", command=self.close_camera,
                                   bg="#757575", fg="white", font=("Arial", 12),
                                   padx=15, pady=5, borderwidth=0)
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam. Please check your camera connection.")
            self.window.destroy()
            return
            
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Start video feed
        self.update_cam()
        
        # Set up window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.close_camera)
        
    def update_cam(self):
        # Get a frame from the webcam
        ret, frame = self.cap.read()
        if ret:
            # Convert frame to format tkinter can display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Update the label
            self.camera_frame.configure(image=img_tk)
            self.camera_frame.image = img_tk
            
            # Store the current frame
            self.current_frame = frame
            
        # Schedule the next update
        self.window.after(10, self.update_cam)
    
    def capture_image(self):
        # Capture the current frame
        if hasattr(self, 'current_frame'):
            # Save the frame as image
            self.callback(self.current_frame)
            self.close_camera()
    
    def close_camera(self):
        # Release the webcam
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        
        # Close the window
        self.window.destroy()

class CartoonifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartoonify Image App")
        self.root.geometry("800x600")
        self.root.configure(bg="#001839")  # Dark blue background as shown in the image

        self.original_image = None
        self.cartoon_image = None
        self.current_filter = None

        # Title label
        self.title_label = Label(root, text="Let's cartoonify your image", font=("Arial", 20), 
                                bg="#001839", fg="white")
        self.title_label.pack(pady=20)

        # Create image source buttons frame first
        self.source_frame = Frame(root, bg="#001839")
        self.source_frame.pack(pady=10)

        # Open Image Button
        self.open_button = Button(self.source_frame, text="Upload Image", command=self.open_image, 
                                 bg="#1976D2", fg="white", font=("Arial", 12),
                                 padx=10, pady=5, borderwidth=0)
        self.open_button.pack(side=tk.LEFT, padx=10)

        # Try to load camera icon for the Camera Button
        try:
            camera_img = Image.open("images\\camera_icon.png")
            camera_img = camera_img.resize((30, 30), Image.LANCZOS)
            self.camera_photo = ImageTk.PhotoImage(camera_img)
            
            self.camera_button = Button(self.source_frame, image=self.camera_photo, command=self.open_camera,
                                      bg="#1976D2", fg="white", borderwidth=0, padx=10, pady=5)
        except Exception as e:
            print(f"Error loading camera icon: {e}")
            # If camera icon can't be loaded, use text instead
            self.camera_button = Button(self.source_frame, text="Camera", command=self.open_camera,
                                      bg="#1976D2", fg="white", font=("Arial", 12),
                                      padx=10, pady=5, borderwidth=0)
        
        self.camera_button.pack(side=tk.LEFT, padx=10)

        # Image display frame (side-by-side with arrow between)
        self.image_frame = Frame(root, bg="#001839")
        self.image_frame.pack(pady=20)

        # Original image container (white square)
        self.panel_original = Label(self.image_frame, bg="white", width=25, height=13)
        self.panel_original.grid(row=0, column=0, padx=10)

        # Arrow between images
        self.arrow_label = Label(self.image_frame, text="→", font=("Arial", 20, "bold"), 
                                bg="#001839", fg="white")
        self.arrow_label.grid(row=0, column=1, padx=10)

        # Cartoonified image container (white square)
        self.panel_cartoon = Label(self.image_frame, bg="white", width=25, height=13)
        self.panel_cartoon.grid(row=0, column=2, padx=10)

        # Filter buttons frame
        self.filter_frame = Frame(root, bg="#001839")
        self.filter_frame.pack(pady=10)

        # Load filter icons
        try:
            # Cartoon filter icon - create rounded appearance
            cartoon_img = Image.open("images\\CartoonFilter.jpg")
            cartoon_img = cartoon_img.resize((60, 60), Image.LANCZOS)
            
            # Create a circular mask
            mask = Image.new("L", cartoon_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, cartoon_img.size[0], cartoon_img.size[1]), fill=255)
            
            # Apply mask to create circular image
            cartoon_circle = Image.new("RGBA", cartoon_img.size)
            cartoon_circle.paste(cartoon_img, (0, 0), mask)
            self.cartoon_photo = ImageTk.PhotoImage(cartoon_circle)
            
            # Sketch filter icon - create rounded appearance
            sketch_img = Image.open("images\\SketchFilter.jpg")
            sketch_img = sketch_img.resize((60, 60), Image.LANCZOS)
            
            # Apply same mask for consistency
            sketch_circle = Image.new("RGBA", sketch_img.size)
            sketch_circle.paste(sketch_img, (0, 0), mask)
            self.sketch_photo = ImageTk.PhotoImage(sketch_circle)
        except Exception as e:
            # If images can't be loaded, create placeholder colors
            self.cartoon_photo = None
            self.sketch_photo = None
            print(f"Error loading filter icons: {e}")

        # Cartoon filter button with rounded icon
        self.cartoon_frame = Frame(self.filter_frame, bg="#001839")
        self.cartoon_frame.grid(row=0, column=0, padx=20)
        
        # Create a container frame without visible border initially
        self.cartoon_container = Frame(self.cartoon_frame, bg="#001839", 
                                      highlightbackground="#001839", highlightthickness=2, bd=0)
        self.cartoon_container.pack(pady=5)
        
        # Use image if available, otherwise use colored background
        if self.cartoon_photo:
            self.cartoon_icon = Label(self.cartoon_container, image=self.cartoon_photo, 
                                     bg="#001839", borderwidth=0)
        else:
            self.cartoon_icon = Label(self.cartoon_container, bg="#FF7043", width=8, height=4, 
                                     borderwidth=0)
        
        self.cartoon_icon.pack()
        self.cartoon_container.bind("<Button-1>", lambda e: self.cartoonify_image())
        self.cartoon_icon.bind("<Button-1>", lambda e: self.cartoonify_image())
        
        self.cartoon_label = Label(self.cartoon_frame, text="Cartoon", bg="#001839", fg="white", font=("Arial", 10))
        self.cartoon_label.pack(pady=5)

        # Sketch filter button with rounded icon
        self.sketch_frame = Frame(self.filter_frame, bg="#001839")
        self.sketch_frame.grid(row=0, column=1, padx=20)
        
        # Create a container frame without visible border initially
        self.sketch_container = Frame(self.sketch_frame, bg="#001839", 
                                     highlightbackground="#001839", highlightthickness=2, bd=0)
        self.sketch_container.pack(pady=5)
        
        # Use image if available, otherwise use colored background
        if self.sketch_photo:
            self.sketch_icon = Label(self.sketch_container, image=self.sketch_photo,
                                    bg="#001839", borderwidth=0)
        else:
            self.sketch_icon = Label(self.sketch_container, bg="#E0E0E0", width=8, height=4, 
                                    borderwidth=0)
        
        self.sketch_icon.pack()
        self.sketch_container.bind("<Button-1>", lambda e: self.sketch_filter())
        self.sketch_icon.bind("<Button-1>", lambda e: self.sketch_filter())
        
        self.sketch_label = Label(self.sketch_frame, text="Sketch", bg="#001839", fg="white", font=("Arial", 10))
        self.sketch_label.pack()

        # Action buttons frame
        self.action_frame = Frame(root, bg="#001839")
        self.action_frame.pack(pady=10)

        # Reset button
        self.reset_button = Button(self.action_frame, text="Reset", command=self.reset_app, 
                                  bg="#1976D2", fg="white", font=("Arial", 12),
                                  padx=15, pady=5, borderwidth=0)
        self.reset_button.grid(row=0, column=0, padx=10)

        # Save button
        self.save_button = Button(self.action_frame, text="Save", command=self.save_image, 
                                 bg="#1976D2", fg="white", font=("Arial", 12),
                                 padx=15, pady=5, borderwidth=0, state='disabled')
        self.save_button.grid(row=0, column=1, padx=10)

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = cv2.imread(file_path)
            self.original_image = image
            self.show_image(image, is_original=True)
            self.save_button.config(state='normal')
    
    def open_camera(self):
        self.camera_window = CameraWindow(self.root, self.process_camera_image)
    
    def process_camera_image(self, image):
        self.original_image = image
        self.show_image(image, is_original=True)
        self.save_button.config(state='normal')

    def show_image(self, cv_img, is_original=True):
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_resized = img_pil.resize((250, 250))
        img_tk = ImageTk.PhotoImage(img_resized)

        if is_original:
            self.panel_original.configure(image=img_tk, width=250, height=250)
            self.panel_original.image = img_tk
        else:
            self.panel_cartoon.configure(image=img_tk, width=250, height=250)
            self.panel_cartoon.image = img_tk

    def cartoonify_image(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        # Highlight the selected filter button
        self.cartoon_container.config(highlightbackground="#4CAF50")  # Green highlight
        self.sketch_container.config(highlightbackground="#FFFFFF")   # Reset sketch button

        img = self.original_image.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray_blur, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, blockSize=9, C=2)
        color = cv2.bilateralFilter(img, d=9, sigmaColor=250, sigmaSpace=250)
        cartoon = cv2.bitwise_and(color, color, mask=edges)

        self.cartoon_image = cartoon
        self.current_filter = "cartoon"
        self.show_image(cartoon, is_original=False)
        self.save_button.config(state='normal')

    def sketch_filter(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        # Highlight the selected filter button
        self.sketch_container.config(highlightbackground="#4CAF50")  # Green highlight
        self.cartoon_container.config(highlightbackground="#FFFFFF")  # Reset cartoon button

        img = cv2.cvtColor(self.original_image.copy(), cv2.COLOR_BGR2GRAY)
        inv = 255 - img
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(img, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

        self.cartoon_image = sketch_bgr
        self.current_filter = "sketch"
        self.show_image(sketch_bgr, is_original=False)
        self.save_button.config(state='normal')

    def oil_paint_filter(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        img = cv2.edgePreservingFilter(self.original_image.copy(), flags=2, sigma_s=60, sigma_r=0.4)
        self.cartoon_image = img
        self.current_filter = "oil_paint"
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
        self.current_filter = None

        # Clear image displays
        self.panel_original.configure(image="", width=25, height=13)
        self.panel_cartoon.configure(image="", width=25, height=13)
        
        # Reset image references
        if hasattr(self.panel_original, 'image'):
            self.panel_original.image = None
        if hasattr(self.panel_cartoon, 'image'):
            self.panel_cartoon.image = None
            
        # Reset filter button highlights - make them invisible again
        self.cartoon_container.config(highlightbackground="#001839")
        self.sketch_container.config(highlightbackground="#001839")
            
        # Disable save button
        self.save_button.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    
    # Hide main window initially
    root.withdraw()
    
    # Show splash screen
    splash = SplashScreen(root)
    
    # Simulate loading time
    root.after(3000, splash.destroy)  # Show splash for 3 seconds
    root.after(2200, root.deiconify)  # Show main window after splash is gone
    
    app = CartoonifyApp(root)
    root.mainloop()