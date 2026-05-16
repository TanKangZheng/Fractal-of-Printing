# Third-Party Packages
import requests
from PIL import Image, ImageTk

# Helper Files
import parsedeck as pd
import printprep as pp

# Python Package
import tkinter as tk
from tkinter import ttk
from io import BytesIO
import threading
from pathlib import Path
import os
import sys

#--- Global Variables ---#
if hasattr(sys, '_MEIPASS'):
    SAVE_FOLDER = os.path.join(os.path.dirname(sys.executable), "Downloads")
else:
    SAVE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fractal of Printing")
        self.geometry("1200x800")
        self.images = []
        self.cache = []

        self._build_layout()

        Path(SAVE_FOLDER).mkdir(parents=True, exist_ok=True)

    def _build_layout(self):
        self.columnconfigure(0, weight=2, minsize=0, uniform="col")
        self.columnconfigure(1, weight=3, minsize=0, uniform="col")
        self.rowconfigure(0, weight=1)

        self._build_left_column()
        self._build_right_column()
        self._build_overlay()

    def _build_left_column(self):
        left = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=0)

        text_frame = tk.Frame(left)
        text_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.text_area = tk.Text(text_frame, wrap=tk.WORD)
        self.text_area.grid(row=0, column=0, sticky="nsew")
        text_scroll = ttk.Scrollbar(text_frame, command=self.text_area.yview)
        text_scroll.grid(row=0, column=1, sticky="ns")
        self.text_area.config(yscrollcommand=text_scroll.set)

        # Scroll wheel bindings for text area
        self.text_area.bind("<MouseWheel>", self._scroll_text)
        self.text_area.bind("<Button-4>", self._scroll_text)
        self.text_area.bind("<Button-5>", self._scroll_text)

        btn_frame = tk.Frame(left)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Buttons on the left
        tk.Button(btn_frame, text="Load Images", command=self.LoadCards).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Download Images", command=self.DownloadImages).pack(side=tk.LEFT, padx=4)

        # Checkboxes stacked vertically on the right
        check_frame = tk.Frame(btn_frame)
        check_frame.pack(side=tk.LEFT, padx=10)

        self.FoilProcessing = tk.BooleanVar(value=False)
        self.Upscale = tk.BooleanVar(value=False)

        tk.Checkbutton(check_frame, text="Foil", variable=self.FoilProcessing).pack(anchor="w")
        tk.Checkbutton(check_frame, text="Upscale", variable=self.Upscale).pack(anchor="w")

    def _build_right_column(self):
        right = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        right.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        self.img_canvas = tk.Canvas(right)
        self.img_canvas.grid(row=0, column=0, sticky="nsew")
        self.img_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.img_canvas.yview)
        self.img_scroll.grid(row=0, column=1, sticky="ns")
        self.img_canvas.config(yscrollcommand=self.img_scroll.set)
        self.img_frame = tk.Frame(self.img_canvas)
        self.img_frame.bind(
            "<Configure>",
            lambda e: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all"))
        )
        self.img_canvas.create_window((0, 0), window=self.img_frame, anchor="nw")

        # Scroll wheel bindings for image canvas
        self.img_canvas.bind("<MouseWheel>", self._scroll_images)
        self.img_canvas.bind("<Button-4>", self._scroll_images)
        self.img_canvas.bind("<Button-5>", self._scroll_images)
        self.img_frame.bind("<MouseWheel>", self._scroll_images)
        self.img_frame.bind("<Button-4>", self._scroll_images)
        self.img_frame.bind("<Button-5>", self._scroll_images)

        # Reflow grid on resize
        self.img_canvas.bind("<Configure>", self.reflow_images)

    def _build_overlay(self):
        self.overlay = tk.Frame(self, bg='black')
        self.overlay_log = tk.Text(
            self.overlay, 
            bg='black', 
            fg='white', 
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.overlay_log.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

    def show_overlay(self):
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay_log.config(state=tk.NORMAL)
        self.overlay_log.delete('1.0', tk.END)
        self.overlay_log.config(state=tk.DISABLED)
        self.overlay.lift()
        self.update()

    def hide_overlay(self):
        self.overlay.place_forget()

    def log_overlay(self, message: str):
        self.after(0, self._write_log, message)

    def _write_log(self, message:str):
        self.overlay_log.config(state=tk.NORMAL)
        self.overlay_log.insert(tk.END, message + '\n')
        self.overlay_log.see(tk.END)  # Auto-scroll to latest
        self.overlay_log.config(state=tk.DISABLED)

    def add_image(self, pil_image):
        img = ImageTk.PhotoImage(pil_image)
        self.images.append(img)  # prevent GC
        tk.Label(self.img_frame, image=img).pack(pady=4)

    def LoadCards(self):
        self.show_overlay()

        def task():
            data = self.text_area.get("1.0", tk.END).splitlines()[0].strip()
            print(data)
            decklist = pd.parseDecklist(data, self._write_log)
            self.cache = decklist
            self._write_log("Loading Card images...")
            self._load_card_images(decklist)

            # Post
            self.after(0, lambda: self._finish_loading())

        threading.Thread(target=task, daemon=True).start()

    def DownloadImages(self):
        self.show_overlay()

        def task():
            data = self.text_area.get("1.0", tk.END).splitlines()[0].strip()
            if (len(self.cache) == 0):
                decklist = pd.parseDecklist(data, self._write_log)
                self.cache = decklist
            for card in self.cache:
                pd.saveImage(card, SAVE_FOLDER, self._write_log)
            if (self.FoilProcessing.get()):
                pp.boost_saturation(SAVE_FOLDER, log_func=self._write_log)
                pp.boost_uniform_vibrancy(SAVE_FOLDER, log_func=self._write_log)
            pp.add_border(SAVE_FOLDER, log_func=self._write_log)
            if (self.Upscale.get()):
                pp.upscale_bordered(SAVE_FOLDER, log_func=self._write_log)

            # Post
            self.after(0, lambda: self._finish_loading())
                
        threading.Thread(target=task, daemon=True).start()

    def _finish_loading(self):
        self.hide_overlay()

    def _load_card_images(self, cardList: list[pd.CardData]):
        for widget in self.img_frame.winfo_children():
            widget.destroy()
        self.images.clear()
        self.raw_images = []  # Store raw PIL images for reflowing

        for card in cardList:
            if card.imgLink is None:
                continue
            try:
                self._write_log(f"Getting image from {card.imgLink}...")
                response = requests.get(card.imgLink)
                img = Image.open(BytesIO(response.content))
                self.raw_images.append(img)
            except Exception as e:
                self._write_log(f"Could not load image for {card.name}: {e}")

        self.reflow_images()

    def reflow_images(self, event=None):
        if not hasattr(self, 'raw_images') or not self.raw_images:
            return

        # Clear existing widgets
        for widget in self.img_frame.winfo_children():
            widget.destroy()
        self.images.clear()

        COLS = 3
        PADDING = 4
        scrollbar_width = self.img_scroll.winfo_width()
        canvas_width = self.img_canvas.winfo_width() - scrollbar_width
        img_width = (canvas_width - (PADDING * (COLS + 1))) // COLS

        for i, pil_img in enumerate(self.raw_images):
            aspect = pil_img.height / pil_img.width
            img_height = int(img_width * aspect)
            resized = pil_img.resize((img_width, img_height), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(resized)
            self.images.append(tk_img)
            row, col = divmod(i, COLS)
            lbl = tk.Label(self.img_frame, image=tk_img)
            lbl.bind("<MouseWheel>", self._scroll_images)
            lbl.bind("<Button-4>", self._scroll_images)
            lbl.bind("<Button-5>", self._scroll_images)
            lbl.grid(row=row, column=col, padx=PADDING, pady=PADDING)

    def _scroll_text(self, event):
        if event.num == 4:
            self.text_area.yview_scroll(-1, "units")
        elif event.num == 5:
            self.text_area.yview_scroll(1, "units")
        else:
            self.text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_images(self, event):
        if event.num == 4:
            self.img_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.img_canvas.yview_scroll(1, "units")
        else:
            self.img_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

if __name__ == "__main__":
    app = App()
    app.mainloop()