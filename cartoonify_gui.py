# Configure custom style
style.configure("Custom.Horizontal.TProgressbar",
                troughcolor='#e0e0e0',
                background='#4caf50',   # green bar
                thickness=10,
                bordercolor='gray',
                lightcolor='#6fcf97',
                darkcolor='#4caf50')

# Create progress bar
self.progress_bar = ttk.Progressbar(self.root,
                                    mode='indeterminate',
                                    length=300,
                                    style="Custom.Horizontal.TProgressbar")

# ✅ Position it right after creating it (so it doesn’t overlap buttons)
self.progress_bar.pack(pady=(20, 0))  # Adjust padding as needed
