import tkinter as tk
from tkinter import Button, Label, filedialog, messagebox, Frame, Toplevel
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance
import os
import urllib.parse
import webbrowser
import requests
import numpy as np
from tkinter import ttk
import random

class CartoonifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartoonify")
        self.root.geometry("800x600")
        self.root.configure(bg="#001839")  # Dark blue background
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")
        
        self.original_image = None
        self.cartoon_image = None
        self.current_filter = None
        self.selected_filter = None
        self.cap = None  # Camera capture object
        self.cartoon_image_path = ""
        self.uploaded_image_url = ""
        
        # Load OpenCV's face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Start with splash screen
        self.show_splash_screen()
    
    def show_splash_screen(self):
        # Clear any existing widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configure the whole window as splash
        self.root.geometry("400x400")
        
        # Center the splash window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 400) // 2
        self.root.geometry(f"400x400+{x}+{y}")
        
        # Create a frame for the splash content
        splash_frame = Frame(self.root, bg="#001839")
        splash_frame.pack(expand=True, fill="both")
        
        # Try to load and display the logo
        try:
            logo_img = Image.open("images\\logo.png")
            # Resize if needed
            logo_img = logo_img.resize((400, 400), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            
            logo_label = Label(splash_frame, image=self.logo_photo, bg="#001839")
            logo_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Error loading logo: {e}")
            # If logo can't be loaded, display text instead
            logo_label = Label(splash_frame, text="Cartoonify", font=("Arial", 30, "bold"), 
                              bg="#001839", fg="white")
            logo_label.pack(pady=(80, 20))
        
        # Schedule transition to main app after delay
        self.root.after(3000, self.transition_to_main_app)
    
    def transition_to_main_app(self):
        # Animate the transition by gradually expanding the window
        self.animate_transition(400, 400, 800, 600, steps=10, target_interface=self.init_main_interface)
    
    def animate_transition(self, start_width, start_height, end_width, end_height, steps=10, target_interface=None):
        def resize_step(current_step):
            if current_step <= steps:
                # Calculate intermediate size
                width = start_width + (end_width - start_width) * current_step // steps
                height = start_height + (end_height - start_height) * current_step // steps
                
                # Center the window
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width - width) // 2
                y = (screen_height - height) // 2
                self.root.geometry(f"{width}x{height}+{x}+{y}")
                
                # Schedule next step
                self.root.after(20, lambda: resize_step(current_step + 1))
            else:
                # Transition complete, show target interface
                if target_interface:
                    target_interface()
        
        # Start the animation
        resize_step(1)
    
    def init_main_interface(self):
        # Clear any existing widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title label
        self.title_label = Label(self.root, text="🎨 Let's Cartoonify Your Image! 🎨", 
                        font=("Segoe UI", 24, "bold"), 
                        bg="#001839", fg= "#FFD93D",
                        relief="flat", bd=0)
        self.title_label.pack(pady=(30, 20))

        # Create image source buttons frame
        self.source_frame = Frame(self.root, bg="#001839")
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
            
            self.camera_button = Button(self.source_frame, image=self.camera_photo, command=self.init_camera_interface,
                                      bg="#1976D2", fg="white", borderwidth=0, padx=10, pady=5)
        except Exception as e:
            print(f"Error loading camera icon: {e}")
            # If camera icon can't be loaded, use text instead
            self.camera_button = Button(self.source_frame, text="Camera", command=self.init_camera_interface,
                                      bg="#1976D2", fg="white", font=("Arial", 12),
                                      padx=10, pady=5, borderwidth=0)
        
        self.camera_button.pack(side=tk.LEFT, padx=10)

        # Image display frame (side-by-side with arrow between)
        self.image_frame = Frame(self.root, bg="#001839")
        self.image_frame.pack(pady=20)

         # ...........................Estimate Age Button..............................
        self.age_button = Button(self.source_frame, text="Estimate Age", command=self.estimate_age,
                         bg="#1976D2", fg="white", font=("Arial", 12),
                         padx=10, pady=5, borderwidth=0)
        self.age_button.pack(side=tk.LEFT, padx=10)

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

        # Beauty rating label (initially empty)
        self.beauty_label = Label(self.image_frame, text="", font=("Arial", 12), 
                                 bg="#001839", fg="white")
        self.beauty_label.grid(row=1, column=0, columnspan=3, pady=10)

        # Filter buttons frame
        self.filter_frame = Frame(self.root, bg="#001839")
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
        if hasattr(self, 'cartoon_photo') and self.cartoon_photo:
            self.cartoon_icon = Label(self.cartoon_container, image=self.cartoon_photo, 
                                     bg="#001839", borderwidth=0)
        else:
            self.cartoon_icon = Label(self.cartoon_container, bg="#FF7043", width=8, height=4, 
                                     borderwidth=0)
        
        self.cartoon_icon.pack()
        self.cartoon_container.bind("<Button-1>", lambda e: self.cartoonify_image())
        self.cartoon_icon.bind("<Button-1>", lambda e: self.show_loading_bar(self.cartoonify_image))
        
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
        if hasattr(self, 'sketch_photo') and self.sketch_photo:
            self.sketch_icon = Label(self.sketch_container, image=self.sketch_photo,
                                    bg="#001839", borderwidth=0)
        else:
            self.sketch_icon = Label(self.sketch_container, bg="#E0E0E0", width=8, height=4, 
                                    borderwidth=0)
        
        self.sketch_icon.pack()
        self.sketch_container.bind("<Button-1>", lambda e: self.sketch_filter())
        self.sketch_icon.bind("<Button-1>", lambda e: self.show_loading_bar(self.sketch_filter))
        
        self.sketch_label = Label(self.sketch_frame, text="Sketch", bg="#001839", fg="white", font=("Arial", 10))
        self.sketch_label.pack()

        # Winx Club filter button with rounded icon
        self.winx_frame = Frame(self.filter_frame, bg="#001839")
        self.winx_frame.grid(row=0, column=2, padx=20)

        self.winx_container = Frame(self.winx_frame, bg="#001839",
                                    highlightbackground="#001839", highlightthickness=2, bd=0)
        self.winx_container.pack(pady=5)

        try:
            winx_img = Image.open("images\\WinxFilter.png")
            winx_img = winx_img.resize((60, 60), Image.LANCZOS)

            # Create circular mask
            mask = Image.new("L", winx_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, winx_img.size[0], winx_img.size[1]), fill=255)

            winx_circle = Image.new("RGBA", winx_img.size)
            winx_circle.paste(winx_img, (0, 0), mask)
            self.winx_photo = ImageTk.PhotoImage(winx_circle)

            self.winx_icon = Label(self.winx_container, image=self.winx_photo, bg="#001839", borderwidth=0)
        except Exception as e:
            print(f"Error loading Winx filter icon: {e}")
            self.winx_icon = Label(self.winx_container, bg="#FFD1DC", width=8, height=4, borderwidth=0)

        self.winx_icon.pack()
        self.winx_container.bind("<Button-1>", lambda e: self.winxclub_filter())
        self.winx_icon.bind("<Button-1>", lambda e: self.show_loading_bar(self.winxclub_filter))

        self.winx_label = Label(self.winx_frame, text="Winx", bg="#001839", fg="white", font=("Arial", 10))
        self.winx_label.pack()

        # Clone filter button with rounded icon
        self.clone_frame = Frame(self.filter_frame, bg="#001839")
        self.clone_frame.grid(row=0, column=3, padx=20)

        self.clone_container = Frame(self.clone_frame, bg="#001839",
                                    highlightbackground="#001839", highlightthickness=2, bd=0)
        self.clone_container.pack(pady=5)

        try:
            # Load Clone filter icon and create rounded appearance
            clone_img = Image.open("images\\CloneFilter.jpg")
            clone_img = clone_img.resize((60, 60), Image.LANCZOS)

            # Reuse the circular mask from earlier
            mask = Image.new("L", clone_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, clone_img.size[0], clone_img.size[1]), fill=255)

            clone_circle = Image.new("RGBA", clone_img.size)
            clone_circle.paste(clone_img, (0, 0), mask)
            self.clone_photo = ImageTk.PhotoImage(clone_circle)

            self.clone_icon = Label(self.clone_container, image=self.clone_photo, bg="#001839", borderwidth=0)
        except Exception as e:
            print(f"Error loading Clone filter icon: {e}")
            self.clone_icon = Label(self.clone_container, bg="#FF00FF", width=8, height=4, borderwidth=0)

        self.clone_icon.pack()
        self.clone_container.bind("<Button-1>", lambda e: self.clone_filter())
        self.clone_icon.bind("<Button-1>", lambda e: self.show_loading_bar(self.clone_filter))

        self.clone_label = Label(self.clone_frame, text="Clone", bg="#001839", fg="white", font=("Arial", 10))
        self.clone_label.pack()

        # Action buttons frame
        self.action_frame = Frame(self.root, bg="#001839")
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
        
        # Share button
        self.share_button = Button(self.action_frame, text="Share", command=self.open_socials_window, 
                                 bg="#1976D2", fg="white", font=("Arial", 12),
                                 padx=15, pady=5, borderwidth=0, state='disabled')
        self.share_button.grid(row=0, column=2, padx=10)

        # Add progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(self.root, mode='indeterminate', length=300)

    def show_loading_bar(self, after_callback=None):
        self.progress_bar.place(relx=0.5, rely=0.95, anchor='center')
        self.progress_bar.start(10)
        if after_callback:
            self.root.after(3000, lambda: [self.hide_loading_bar(), after_callback()])
        else:
            self.root.after(3000, self.hide_loading_bar)

    def on_filter_selected(self, filter_name):
        self.selected_filter = filter_name
        self.show_loading_bar()
        # After 3 seconds, apply the filter
        self.root.after(3000, self.apply_selected_filter)

    def hide_loading_bar(self):
        self.progress_bar.stop()
        self.progress_bar.place_forget()
   
    def apply_selected_filter(self):
        self.hide_loading_bar()

        if self.original_image is None or self.selected_filter is None:
            return

        if self.selected_filter == 'cartoon':
            filtered = self.cartoonify_image(process_only=True)
        elif self.selected_filter == 'sketch':
            filtered = self.sketch_filter(process_only=True)
        elif self.selected_filter == 'winxclub':
            filtered = self.winxclub_filter(process_only=True)
        elif self.selected_filter == 'clone':
            filtered = self.clone_filter(process_only=True)
        else:
            return

        # Show filtered image on panel_cartoon
        self.display_filtered_image(filtered)

    def hide_loading_bar(self):
        self.progress_bar.stop()
        self.progress_bar.place_forget()

    def init_camera_interface(self):
        # First animate closing the main interface
        self.animate_transition(800, 600, 680, 520, steps=10, target_interface=self.show_camera_interface)
    
    def show_camera_interface(self):
        # Clear any existing widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configure camera window
        self.root.title("Camera")
        
        # Add a title
        title_label = Label(self.root, text="Camera Preview", font=("Arial", 16), bg="#001839", fg="white")
        title_label.pack(pady=10)
        
        # Camera preview frame
        self.camera_frame = Label(self.root, bg="black", width=640, height=480)
        self.camera_frame.pack(pady=10)
        
        # Buttons frame
        buttons_frame = Frame(self.root, bg="#001839")
        buttons_frame.pack(pady=10)
        
        # Capture button
        self.capture_button = Button(buttons_frame, text="Capture", command=self.capture_image,
                                    bg="#1976D2", fg="white", font=("Arial", 12),
                                    padx=15, pady=5, borderwidth=0)
        self.capture_button.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        self.cancel_button = Button(buttons_frame, text="Cancel", command=self.return_to_main,
                                   bg="#757575", fg="white", font=("Arial", 12),
                                   padx=15, pady=5, borderwidth=0)
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam. Please check your camera connection.")
            self.return_to_main()
            return
            
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Start video feed
        self.update_cam()
    
    def update_cam(self):
        # Check if we're still in camera mode
        if not hasattr(self, 'camera_frame') or not self.cap or not self.cap.isOpened():
            return
            
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
        self.root.after(10, self.update_cam)
    
    def capture_image(self):
        # Capture the current frame
        if hasattr(self, 'current_frame'):
            # Save the frame as image
            self.original_image = self.current_frame.copy()
            self.release_camera()  # Release camera resources
            # Transition back to main interface
            self.animate_transition(680, 520, 800, 600, steps=10, target_interface=self.return_to_main_with_image)
    
    def return_to_main(self):
        self.release_camera()  # Release camera resources
        # Transition back to main interface
        self.animate_transition(680, 520, 800, 600, steps=10, target_interface=self.init_main_interface)
    
    def return_to_main_with_image(self):
        self.init_main_interface()  # Set up the main interface
        # Show the captured image
        self.show_image(self.original_image, is_original=True)
        self.save_button.config(state='normal')
        self.share_button.config(state='normal')
        # Analyze the face for beauty rating
        self.analyze_face()
    
    def release_camera(self):
        # Release the webcam resources
        if hasattr(self, 'cap') and self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = cv2.imread(file_path)
            self.original_image = image
            self.show_image(image, is_original=True)
            self.save_button.config(state='normal')
            self.share_button.config(state='normal')
            # Analyze the face for beauty rating
            self.analyze_face()

             #.................ESTIMATE AGE..........................

     def estimate_age(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        # Convert PIL image to OpenCV format
        cv_image = cv2.cvtColor(np.array(self.original_image), cv2.COLOR_RGB2BGR)

        # Detect faces
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) == 0:
            messagebox.showerror("Error", "Face is not recognized.")
            return

        # For simplicity, use the first face
        (x, y, w, h) = faces[0]
        face_img = cv_image[y:y+h, x:x+w]

        # Fake age estimate (placeholder)
        estimated_age = self.mock_age_estimator(face_img)

        # Draw age label on image
        labeled_img = cv_image.copy()
        cv2.putText(labeled_img, f"Age: {estimated_age}", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.rectangle(labeled_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert back to PIL and show in original panel
        labeled_img_rgb = cv2.cvtColor(labeled_img, cv2.COLOR_BGR2RGB)
        labeled_pil = Image.fromarray(labeled_img_rgb)
        self.display_image_on_panel(labeled_pil, self.panel_original)

    def mock_age_estimator(self, face_image):
        return random.randint(18, 60)

    def display_image_on_panel(self, image, panel):
        image_resized = image.resize((300, 250), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image_resized)
        panel.configure(image=photo)
        panel.image = photo  # Keep a reference
    
    def analyze_face(self):
        if self.original_image is None:
            return
        
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            self.beauty_label.config(text="No face detected", fg="red")
            return
        
        # Get the first face
        (x, y, w, h) = faces[0]
        img_height, img_width = gray.shape
        
        # Calculate face position (center of image = ideal)
        face_center_x = x + w/2
        face_center_y = y + h/2
        
        # Score 1: How centered the face is (0-1)
        center_score = 1 - (abs(face_center_x/img_width - 0.5) + abs(face_center_y/img_height - 0.5))
        
        # Score 2: Face size ratio (ideal ~30% of image area)
        face_ratio = (w * h) / (img_width * img_height)
        size_score = min(1, max(0, face_ratio / 0.3))  # Normalize to 0-1
        
        # Combine scores (60% centering, 40% size)
        beauty_score = int((center_score * 0.6 + size_score * 0.4) * 100)
        
        # Rating text
        if beauty_score >= 85:
            rating = "Gorgeous! 😍"
            color = "#4CAF50"  # Green
        elif beauty_score >= 70:
            rating = "Beautiful! 😊"
            color = "#8BC34A"  # Light green
        elif beauty_score >= 50:
            rating = "Pretty! 🙂"
            color = "#FFC107"  # Yellow
        else:
            rating = "Average"
            color = "#FF9800"  # Orange
        
        self.beauty_label.config(
            text=f"Quality Rating: {beauty_score}% - {rating}", 
            fg=color
        )
    
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
        self.sketch_container.config(highlightbackground="#001839")   # Reset sketch button
        self.winx_container.config(highlightbackground="#001839")     # Reset winx button
        self.clone_container.config(highlightbackground="#001839")     # Reset clone button

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
        self.share_button.config(state='normal')

    def sketch_filter(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        # Highlight the selected filter button
        self.sketch_container.config(highlightbackground="#4CAF50")   # Green highlight
        self.cartoon_container.config(highlightbackground="#001839")  # Reset cartoon button
        self.winx_container.config(highlightbackground="#001839")     # Reset winx button
        self.clone_container.config(highlightbackground="#001839")     # Reset clone button

        img_gray = cv2.cvtColor(self.original_image.copy(), cv2.COLOR_BGR2GRAY)
        sketch = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 9, 10)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)


        self.cartoon_image = sketch_bgr
        self.current_filter = "sketch"
        self.show_image(sketch_bgr, is_original=False)
        self.save_button.config(state='normal')
        self.share_button.config(state='normal')
    
    def winxclub_filter(self):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        # Highlight the selected filter button
        self.winx_container.config(highlightbackground="#4CAF50")     # Green highlight
        self.cartoon_container.config(highlightbackground="#001839")  # Reset cartoon button
        self.sketch_container.config(highlightbackground="#001839")   # Reset sketch button
        self.clone_container.config(highlightbackground="#001839")     # Reset clone button

        # Convert to RGB if it's a NumPy array (OpenCV format)
        if isinstance(self.original_image, np.ndarray):
            img = self.original_image.copy()
        else:
            img = np.array(self.original_image)

        # Apply a Winx-style dreamy effect using HSV adjustments
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Boost saturation and value slightly
        s = cv2.add(s, 30)
        v = cv2.add(v, 20)

        hsv_modified = cv2.merge([h, s, v])
        winx_img = cv2.cvtColor(hsv_modified, cv2.COLOR_HSV2BGR)

        # Display the result
        self.cartoon_image = winx_img
        self.current_filter = "winxclub"
        self.show_image(winx_img, is_original=False)
        self.save_button.config(state='normal')
        self.share_button.config(state='normal')

    def clone_filter(self):
        """Apply clone filter effect with multiple copies of the person"""
        if not hasattr(self, 'original_image') or self.original_image is None:
            print("No image loaded")
            return
        
        try:
            # Highlight the selected filter button
            self.clone_container.config(highlightbackground="#4CAF50")     # Green highlight
            self.cartoon_container.config(highlightbackground="#001839")  # Reset cartoon button
            self.sketch_container.config(highlightbackground="#001839")   # Reset sketch button
            self.winx_container.config(highlightbackground="#001839")     # Reset winx button
            
            # Convert PIL to OpenCV format
            if isinstance(self.original_image, np.ndarray):
                cv_image = self.original_image.copy()
            else:
                cv_image = cv2.cvtColor(np.array(self.original_image), cv2.COLOR_RGB2BGR)
            
            height, width = cv_image.shape[:2]
            
            # Create a larger canvas to fit multiple clones
            canvas_width = int(width * 1.3)
            canvas_height = int(height * 1.1)
            canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
            
            # Fill canvas with a simple background color (you can modify this)
            canvas[:] = [20, 20, 40]  # Dark blue background
            
            # Use simple background subtraction for person detection
            # Convert to grayscale for processing
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Create a simple mask by assuming the person is in the center area
            # This is a simplified approach - for better results, you'd use ML models
            mask = np.zeros(gray.shape, dtype=np.uint8)
            
            # Create a rough person mask using edge detection and morphology
            edges = cv2.Canny(gray, 50, 150)
            
            # Use morphological operations to create a person-like shape
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            edges = cv2.morphologyEx(edges, cv2.MORPH_DILATE, kernel, iterations=3)
            
            # Find the largest contour (assuming it's the person)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get the largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Create mask from the largest contour
                cv2.fillPoly(mask, [largest_contour], 255)
                
                # Smooth the mask
                mask = cv2.GaussianBlur(mask, (5, 5), 0)
            else:
                # Fallback: use center region as person
                center_x, center_y = width // 2, height // 2
                cv2.ellipse(mask, (center_x, center_y), (width//3, height//2), 0, 0, 360, 255, -1)
            
            # Extract the person using the mask
            person_masked = cv_image.copy()
            mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
            person_masked = (person_masked * mask_3channel).astype(np.uint8)
            
            # Define positions for clones
            clone_positions = [
                (canvas_width//2 - width//2, canvas_height//2 - height//2),  # Center (original)
                (50, canvas_height//2 - height//2),                         # Left
                (canvas_width - width - 50, canvas_height//2 - height//2),  # Right
            ]
            
            # Add some variation to clone positions
            if canvas_height > height + 100:
                clone_positions.extend([
                    (canvas_width//4 - width//4, 20),                       # Top left
                    (3*canvas_width//4 - width//4, 20),                     # Top right
                ])
            
            # Place clones on canvas
            for i, (x, y) in enumerate(clone_positions):
                if x >= 0 and y >= 0 and x + width <= canvas_width and y + height <= canvas_height:
                    
                    # Create a slight variation for each clone
                    clone_img = person_masked.copy()
                    current_mask = mask.copy()  # Keep track of current mask
                    
                    if i > 0:  # Don't modify the center/original
                        # Add slight color variations
                        hsv = cv2.cvtColor(clone_img, cv2.COLOR_BGR2HSV)
                        
                        # Vary hue slightly
                        hue_shift = random.randint(-20, 20)
                        hsv[:, :, 0] = cv2.add(hsv[:, :, 0], hue_shift)
                        
                        # Vary saturation
                        sat_mult = random.uniform(0.8, 1.2)
                        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], sat_mult)
                        
                        clone_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                        
                        # Slightly scale some clones
                        if i % 2 == 0:
                            scale_factor = random.uniform(0.9, 1.1)
                            new_width = int(width * scale_factor)
                            new_height = int(height * scale_factor)
                            
                            # Resize both the image and mask together
                            clone_img = cv2.resize(clone_img, (new_width, new_height))
                            current_mask = cv2.resize(current_mask, (new_width, new_height))
                            
                            # Adjust position to center the scaled clone
                            x_offset = (width - new_width) // 2
                            y_offset = (height - new_height) // 2
                            x += x_offset
                            y += y_offset
                            
                            # Update dimensions for placement
                            width_to_use = new_width
                            height_to_use = new_height
                        else:
                            width_to_use = width
                            height_to_use = height
                    else:
                        width_to_use = width
                        height_to_use = height
                    
                    # Ensure clone fits in canvas - fix boundary checking
                    if x < 0:
                        x = 0
                    if y < 0:
                        y = 0
                        
                    end_x = min(canvas_width, x + width_to_use)
                    end_y = min(canvas_height, y + height_to_use)
                    
                    # Calculate actual dimensions that will fit
                    actual_width = end_x - x
                    actual_height = end_y - y
                    
                    if actual_width > 0 and actual_height > 0:
                        # Get the regions that match in size
                        canvas_region = canvas[y:end_y, x:end_x]
                        clone_region = clone_img[:actual_height, :actual_width]
                        mask_region = current_mask[:actual_height, :actual_width]
                        
                        # Ensure all regions have the same shape
                        if (canvas_region.shape[:2] == clone_region.shape[:2] == mask_region.shape and
                            canvas_region.shape[2] == clone_region.shape[2] == 3):
                            
                            # Create alpha mask for smooth blending
                            clone_mask_3d = cv2.cvtColor(mask_region, cv2.COLOR_GRAY2BGR) / 255.0
                            
                            # Ensure mask dimensions match
                            if clone_mask_3d.shape == canvas_region.shape:
                                blended = canvas_region * (1 - clone_mask_3d) + clone_region * clone_mask_3d
                                canvas[y:end_y, x:end_x] = blended.astype(np.uint8)
                            else:
                                print(f"Shape mismatch in blending: canvas {canvas_region.shape}, mask {clone_mask_3d.shape}")
                        else:
                            print(f"Shape mismatch: canvas {canvas_region.shape}, clone {clone_region.shape}, mask {mask_region.shape}")
            
            # Store the result and display using your existing method
            self.cartoon_image = canvas
            self.current_filter = "clone"
            self.show_image(canvas, is_original=False)
            
            # Enable save and share buttons
            if hasattr(self, 'save_button'):
                self.save_button.config(state='normal')
            if hasattr(self, 'share_button'):
                self.share_button.config(state='normal')
                
            print("Clone filter applied successfully!")
            
        except Exception as e:
            print(f"Error applying clone filter: {e}")
            import traceback
            traceback.print_exc()

    def save_image(self):
        if self.cartoon_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.cartoon_image)
                self.cartoon_image_path = file_path  # Store the path for sharing
                messagebox.showinfo("Saved", "Image saved successfully!")

    def upload_to_gofile(self, file_path):
        try:
            # Get upload servers
            server_res = requests.get("https://api.gofile.io/servers")
            if server_res.status_code != 200:
                raise Exception(f"Failed to get server: {server_res.status_code}")

            server_data = server_res.json()
            servers = server_data.get("data", {}).get("servers", [])
            server = servers[0]["name"] if servers else None
            if not server:
                raise Exception("No server available from GoFile")

            # Upload image
            with open(file_path, 'rb') as f:
                files = {'file': f}
                upload_res = requests.post(f"https://{server}.gofile.io/uploadFile", files=files)

            if upload_res.status_code != 200 or not upload_res.content:
                raise Exception("Empty or bad response from upload endpoint")

            try:
                upload_data = upload_res.json()
            except ValueError:
                raise Exception("Could not decode upload response (not valid JSON)")

            if upload_data.get("status") != "ok":
                raise Exception(f"Upload failed: {upload_data.get('message')}")

            download_link = upload_data['data']['downloadPage']
            return download_link

        except Exception as e:
            messagebox.showerror("Upload Error", f"Something went wrong:\n{e}")
            return None

    def open_socials_window(self):
        if not hasattr(self, 'cartoon_image_path') or not self.cartoon_image_path or not os.path.exists(self.cartoon_image_path):
            # If no saved file, save it first
            self.save_image()
            if not hasattr(self, 'cartoon_image_path') or not self.cartoon_image_path:
                return  # User cancelled save

        # Upload to GoFile and get URL
        self.uploaded_image_url = self.upload_to_gofile(self.cartoon_image_path)
        if not self.uploaded_image_url:
            return

        socials = Toplevel(self.root)
        socials.title("Share on Socials")
        socials.geometry("400x280")
        socials.config(bg="white")

        tk.Label(socials, text="✅ Image uploaded successfully!", font=("Arial", 12), fg="green", bg="white").pack(pady=10)
        tk.Label(socials, text="Now you can share it on socials:", font=("Arial", 10), bg="white").pack(pady=5)

        Button(socials, text="📤 Share on WhatsApp", command=self.share_on_whatsapp, width=30).pack(pady=5)
        Button(socials, text="🐦 Share on Twitter", command=self.share_on_twitter, width=30).pack(pady=5)
        Button(socials, text="📧 Share via Email", command=self.share_via_email, width=30).pack(pady=5)

    def share_on_whatsapp(self):
        if hasattr(self, 'uploaded_image_url') and self.uploaded_image_url:
            message = f"Check out this cartoon image I made! 🤩 {self.uploaded_image_url}"
            url = "https://web.whatsapp.com/send?text=" + urllib.parse.quote(message)
            webbrowser.open(url)

    def share_on_twitter(self):
        if hasattr(self, 'uploaded_image_url') and self.uploaded_image_url:
            message = f"Just cartoonified my photo! 😎 Check it out: {self.uploaded_image_url} #CartoonifyApp"
            url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(message)
            webbrowser.open(url)

    def share_via_email(self):
        if hasattr(self, 'uploaded_image_url') and self.uploaded_image_url:
            subject = urllib.parse.quote("Check out my Cartoonified Image! 🎨")
            
            # Plain text format that works better with email clients
            plain_body = f"""Hey there! 👋

    I just created this awesome cartoon image using CartoonifyApp and wanted to share it with you!

    🔗 VIEW MY CARTOON IMAGE:
    {self.uploaded_image_url}

    👆 Just click the link above to see it!

    (If the link doesn't work, copy and paste it into your browser)

    Hope you like it! 😊

    ---
    Created with CartoonifyApp"""
            
            body = urllib.parse.quote(plain_body)
            webbrowser.open(f"mailto:?subject={subject}&body={body}")
            
    def reset_app(self):
        self.original_image = None
        self.cartoon_image = None
        self.current_filter = None
        self.cartoon_image_path = ""
        self.uploaded_image_url = ""

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
        self.winx_container.config(highlightbackground="#001839")
            
        # Disable save and share buttons
        self.save_button.config(state='disabled')
        self.share_button.config(state='disabled')
        
        # Clear beauty rating
        self.beauty_label.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = CartoonifyApp(root)
    root.mainloop()
