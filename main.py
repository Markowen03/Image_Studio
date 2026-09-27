import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import os
from PIL import Image, ImageTk
from rembg import remove, new_session
import easyocr


os.makedirs("images", exist_ok=True)
os.makedirs("output", exist_ok=True)


preview_image = None
rembg_session = None


COLORS = {
    "bg": "#0f172a",          
    "surface": "#1e293b",     
    "surface_alt": "#273449", 
    "border": "#334155",      
    "text": "#f1f5f9",       
    "text_dim": "#94a3b8",    
    "accent": "#6366f1",      
    "accent_hover": "#818cf8",
    "accent_dark": "#4f46e5", 
    "success": "#22c55e",
    "danger": "#ef4444",
    "danger_hover": "#f87171",
}

FONT_FAMILY = "Segoe UI"



class ModernButton(tk.Canvas):
    """A flat, rounded, hover-animated button drawn on a Canvas."""

    def __init__(self, parent, text, command, icon="",
                 bg=COLORS["surface_alt"], hover=COLORS["accent"],
                 fg=COLORS["text"], width=260, height=48,
                 font_size=12, bold=False, radius=14):

        super().__init__(
            parent, width=width, height=height,
            bg=parent["bg"], highlightthickness=0, bd=0,
            cursor="hand2"
        )

        self.command = command
        self.bg_normal = bg
        self.bg_hover = hover
        self.fg = fg
        self.width = width
        self.height = height
        self.radius = radius
        self.text = f"{icon}   {text}" if icon else text
        self.font = (FONT_FAMILY, font_size, "bold" if bold else "normal")

        self._draw(self.bg_normal)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, color):
        self.delete("all")
        self._round_rect(
            2, 2, self.width - 2, self.height - 2,
            self.radius, fill=color, outline=""
        )
        self.create_text(
            self.width / 2, self.height / 2,
            text=self.text, fill=self.fg, font=self.font
        )

    def _on_enter(self, _event):
        self._draw(self.bg_hover)

    def _on_leave(self, _event):
        self._draw(self.bg_normal)

    def _on_click(self, _event):
        if self.command:
            self.command()

    def set_enabled(self, enabled: bool):
        if enabled:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", self._on_click)
            self._draw(self.bg_normal)
        else:
            self.configure(cursor="arrow")
            self.unbind("<Button-1>")
            self._draw(COLORS["border"])



def display_image(image_path):
    global preview_image

    try:
        image = Image.open(image_path)
        image.thumbnail((380, 300))
        preview_image = ImageTk.PhotoImage(image)

        preview_label.config(image=preview_image, text="")

    except Exception as e:
        messagebox.showerror("Preview Error", f"Could not display image:\n\n{e}")


def set_status(message, kind="normal"):
    color = {
        "normal": COLORS["text_dim"],
        "success": COLORS["success"],
        "error": COLORS["danger"],
        "busy": COLORS["accent_hover"],
    }.get(kind, COLORS["text_dim"])

    status_label.config(text=message, fg=color)
    root.update_idletasks()



def capture_image():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        messagebox.showerror("Error", "Cannot access the camera.")
        return

    set_status("Camera opened — click Capture to take a photo.", "busy")

    camera_window = tk.Toplevel(root)
    camera_window.title("Camera")
    camera_window.geometry("700x600")
    camera_window.configure(bg=COLORS["bg"])
    camera_window.resizable(False, False)

    camera_card = tk.Frame(camera_window, bg=COLORS["surface"])
    camera_card.pack(fill="both", expand=True, padx=16, pady=16)

    camera_label = tk.Label(camera_card, bg=COLORS["surface"])
    camera_label.pack(pady=16)

    btn_row = tk.Frame(camera_card, bg=COLORS["surface"])
    btn_row.pack(pady=10)

    camera_frame = {"frame": None}

    def update_camera():
        ret, frame = camera.read()

        if ret:
            camera_frame["frame"] = frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image.thumbnail((640, 440))
            photo = ImageTk.PhotoImage(image)
            camera_label.config(image=photo)
            camera_label.image = photo

        if camera_window.winfo_exists():
            camera_window.after(10, update_camera)

    def take_photo():
        frame = camera_frame["frame"]

        if frame is None:
            messagebox.showerror("Error", "Camera frame not available.")
            return

        filename = "images/captured.jpg"
        cv2.imwrite(filename, frame)
        camera.release()
        camera_window.destroy()

        display_image(filename)
        set_status("Image captured successfully!", "success")
        messagebox.showinfo("Success", "Image captured successfully!")

    def cancel_camera():
        camera.release()
        camera_window.destroy()
        set_status("Camera cancelled.")

    ModernButton(
        btn_row, "Capture", take_photo, icon="📷",
        bg=COLORS["accent"], hover=COLORS["accent_hover"],
        width=200, height=46, bold=True
    ).pack(side="left", padx=8)

    ModernButton(
        btn_row, "Cancel", cancel_camera,
        bg=COLORS["danger"], hover=COLORS["danger_hover"],
        width=140, height=46
    ).pack(side="left", padx=8)

    camera_window.protocol("WM_DELETE_WINDOW", cancel_camera)

    update_camera()


def remove_background():
    global rembg_session

    input_path = "images/captured.jpg"
    output_path = "output/no_background.png"

    if not os.path.exists(input_path):
        messagebox.showerror("Error", "Please capture an image first.")
        return

    try:
        set_status("Preparing background removal...", "busy")

        if rembg_session is None:
            set_status("Loading lightweight AI model...", "busy")
            rembg_session = new_session("u2netp")

        set_status("Removing background...", "busy")

        with open(input_path, "rb") as input_file:
            input_image = input_file.read()

        output_image = remove(input_image, session=rembg_session)

        with open(output_path, "wb") as output_file:
            output_file.write(output_image)

        display_image(output_path)
        set_status("Background removed successfully!", "success")

        messagebox.showinfo(
            "Success",
            "Background removed successfully!\n\nSaved to:\noutput/no_background.png"
        )

    except Exception as e:
        set_status("Background removal failed.", "error")
        messagebox.showerror("Error", f"Background removal failed:\n\n{e}")


def extract_text():

    input_path = "images/captured.jpg"
    output_path = "output/extracted_text.txt"

    if not os.path.exists(input_path):
        messagebox.showerror("Error", "Please capture an image first.")
        return

    try:
        set_status("Extracting text...", "busy")

        reader = easyocr.Reader(["en"], gpu=False)
        result = reader.readtext(input_path, detail=0)
        text = "\n".join(result)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)

        text_output.delete("1.0", tk.END)

        if text.strip():
            text_output.insert(tk.END, text)
            set_status("Text extraction completed!", "success")
        else:
            text_output.insert(tk.END, "No text detected.")
            set_status("No text detected.", "error")

        messagebox.showinfo(
            "OCR Complete",
            "Text extraction completed!\n\nSaved to:\noutput/extracted_text.txt"
        )

    except Exception as e:
        set_status("Text extraction failed.", "error")
        messagebox.showerror("Error", f"Text extraction failed:\n\n{e}")


def convert_to_pixel_art():

    input_path = "images/captured.jpg"
    output_path = "output/pixel_art.png"

    if not os.path.exists(input_path):
        messagebox.showerror("Error", "Please capture an image first.")
        return

    try:
        set_status("Creating pixel art...", "busy")

        image = Image.open(input_path)
        pixel_size = 64

        small_image = image.resize((pixel_size, pixel_size), Image.Resampling.NEAREST)
        pixel_art = small_image.resize(image.size, Image.Resampling.NEAREST)
        pixel_art.save(output_path)

        display_image(output_path)
        set_status("Pixel art created successfully!", "success")

        messagebox.showinfo(
            "Success",
            "Pixel art created successfully!\n\nSaved to:\noutput/pixel_art.png"
        )

    except Exception as e:
        set_status("Pixel art conversion failed.", "error")
        messagebox.showerror("Error", f"Pixel art conversion failed:\n\n{e}")


def clear_output():
    global preview_image

    preview_image = None
    preview_label.config(image="", text="No output yet")
    text_output.delete("1.0", tk.END)
    set_status("Ready")



root = tk.Tk()
root.title("Mark Owen Badua")
root.geometry("960x680")
root.configure(bg=COLORS["bg"])
root.resizable(False, False)



header = tk.Frame(root, bg=COLORS["bg"])
header.pack(fill="x", padx=30, pady=(28, 10))

title = tk.Label(
    header, text="STUDIO NI OWEN",
    font=(FONT_FAMILY, 22, "bold"),
    bg=COLORS["bg"], fg=COLORS["text"]
)
title.pack(anchor="w")

subtitle = tk.Label(
    header, text="Capture · Remove Background · Extract Text · Pixelate",
    font=(FONT_FAMILY, 11),
    bg=COLORS["bg"], fg=COLORS["text_dim"]
)
subtitle.pack(anchor="w", pady=(2, 0))


main_frame = tk.Frame(root, bg=COLORS["bg"])
main_frame.pack(fill="both", expand=True, padx=30, pady=10)



left_card = tk.Frame(main_frame, bg=COLORS["surface"], padx=22, pady=22)
left_card.pack(side="left", fill="y")

tk.Label(
    left_card, text="TOOLS", font=(FONT_FAMILY, 11, "bold"),
    bg=COLORS["surface"], fg=COLORS["text_dim"]
).pack(anchor="w", pady=(0, 14))

ModernButton(
    left_card, "Capture Image", capture_image, icon="📷",
    bg=COLORS["accent"], hover=COLORS["accent_hover"],
    fg="#ffffff", width=248, height=48, bold=True
).pack(pady=6)

ModernButton(
    left_card, "Remove Background", remove_background, icon="🪄",
    width=248, height=48
).pack(pady=6)

ModernButton(
    left_card, "Extract Text", extract_text, icon="🔤",
    width=248, height=48
).pack(pady=6)

ModernButton(
    left_card, "Convert to Pixel Art", convert_to_pixel_art, icon="🎮",
    width=248, height=48
).pack(pady=6)


tk.Frame(left_card, bg=COLORS["border"], height=1).pack(fill="x", pady=16)

ModernButton(
    left_card, "Clear Output", clear_output,
    bg=COLORS["surface_alt"], hover=COLORS["border"],
    width=248, height=42, font_size=11
).pack(pady=6)

ModernButton(
    left_card, "Exit", root.destroy,
    bg=COLORS["danger"], hover=COLORS["danger_hover"],
    fg="#ffffff", width=248, height=42, font_size=11
).pack(pady=6)


right_card = tk.Frame(main_frame, bg=COLORS["surface"], padx=24, pady=22)
right_card.pack(side="left", fill="both", expand=True, padx=(20, 0))

tk.Label(
    right_card, text="OUTPUT PREVIEW", font=(FONT_FAMILY, 11, "bold"),
    bg=COLORS["surface"], fg=COLORS["text_dim"]
).pack(anchor="w")

preview_frame = tk.Frame(
    right_card, bg=COLORS["surface_alt"],
    width=420, height=300, highlightbackground=COLORS["border"],
    highlightthickness=1
)
preview_frame.pack(pady=(10, 18))
preview_frame.pack_propagate(False)

preview_label = tk.Label(
    preview_frame, text="No output yet",
    font=(FONT_FAMILY, 12), bg=COLORS["surface_alt"], fg=COLORS["text_dim"]
)
preview_label.pack(expand=True)

tk.Label(
    right_card, text="EXTRACTED TEXT", font=(FONT_FAMILY, 11, "bold"),
    bg=COLORS["surface"], fg=COLORS["text_dim"]
).pack(anchor="w")

text_wrap = tk.Frame(
    right_card, bg=COLORS["surface_alt"],
    highlightbackground=COLORS["border"], highlightthickness=1
)
text_wrap.pack(fill="both", expand=True, pady=(10, 0))

text_output = tk.Text(
    text_wrap, height=6, font=(FONT_FAMILY, 10),
    bg=COLORS["surface_alt"], fg=COLORS["text"],
    insertbackground=COLORS["text"], relief="flat",
    padx=10, pady=10, wrap="word", bd=0
)
text_output.pack(fill="both", expand=True)


status_bar = tk.Frame(root, bg=COLORS["surface"])
status_bar.pack(fill="x", side="bottom")

status_label = tk.Label(
    status_bar, text="Ready", font=(FONT_FAMILY, 10),
    bg=COLORS["surface"], fg=COLORS["text_dim"], anchor="w"
)
status_label.pack(fill="x", padx=20, pady=10)


root.mainloop()