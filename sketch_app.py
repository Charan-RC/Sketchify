import cv2
import pathlib
import customtkinter as ctk
from tkinter import filedialog
from PIL import ImageTk, Image

class SketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sketch Creator")
        self.root.geometry("1000x600")
        ctk.set_appearance_mode("dark")  # "light" or "dark"
        ctk.set_default_color_theme("blue")  # themes: "blue", "green", "dark-blue"

        # Image variables
        self.image_path = ""
        self.sketch_img = None
        self.width, self.height = 700, 500

        # Sidebar Frame
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Buttons
        ctk.CTkButton(sidebar, text="Open Image", command=self.open_image).pack(pady=10)
        ctk.CTkButton(sidebar, text="Create Sketch", command=self.create_sketch).pack(pady=10)
        ctk.CTkButton(sidebar, text="Save Sketch", command=self.save_image).pack(pady=10)
        ctk.CTkButton(sidebar, text="Reset", command=self.clear_screen).pack(pady=10)
        ctk.CTkButton(sidebar, text="Exit", command=self.root.destroy).pack(pady=10)

        # Intensity Slider
        self.intensity = ctk.CTkSlider(
            sidebar, from_=50, to=300, number_of_steps=50,
            command=lambda v: self.create_sketch()
        )
        self.intensity.set(150)
        self.intensity.pack(pady=20)
        self.intensity_label = ctk.CTkLabel(sidebar, text="Sketch Intensity")
        self.intensity_label.pack()

        # Theme Toggle
        ctk.CTkSwitch(sidebar, text="Dark Mode", command=self.toggle_theme).pack(pady=20)

        # Main Display Frame
        self.display_frame = ctk.CTkFrame(self.root, width=self.width, height=self.height, corner_radius=20)
        self.display_frame.pack(pady=20, padx=20, expand=True, fill="both")

        self.image_label = ctk.CTkLabel(self.display_frame, text="No image loaded")
        self.image_label.pack(expand=True)

    def resize_keep_aspect(self, img, target_w, target_h):
        h, w = img.shape[:2]
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(img, (new_w, new_h))

    def open_image(self):
        self.clear_screen()
        self.image_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if self.image_path:
            self.show_image(self.image_path)

    def show_image(self, img_path):
        image = Image.open(img_path)
        image.thumbnail((self.width, self.height))  # keep aspect ratio
        self.tk_img = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.tk_img, text="")

    def create_sketch(self):
        if not self.image_path:
            return

        img = cv2.imread(self.image_path)
        img = self.resize_keep_aspect(img, self.width, self.height)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(gray)

        smooth = cv2.GaussianBlur(inv, (21, 21), sigmaX=0, sigmaY=0)

        # Contrast controlled by slider
        scale_val = self.intensity.get()
        sketch = cv2.divide(gray, 255 - smooth, scale=scale_val)

        self.sketch_img = sketch
        result_image = Image.fromarray(sketch)
        self.tk_img = ImageTk.PhotoImage(result_image)
        self.image_label.configure(image=self.tk_img, text="")

    def save_image(self):
        if self.sketch_img is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
        )
        if file_path:
            cv2.imwrite(file_path, self.sketch_img)

    def clear_screen(self):
        self.image_label.configure(image="", text="No image loaded")
        self.image_path = ""
        self.sketch_img = None

    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if mode == "Dark" else "Dark")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SketchApp(root)
    root.mainloop()