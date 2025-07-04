import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import random, io, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

MAIN_CARD_W = 180
MAIN_CARD_H = 240
MAIN_GRID_COLS = 6
MAIN_GRID_PADX = 10
MAIN_GRID_PADY = 23
MAIN_FONT = ("Arial", 18)

PDF_CARD_W = 115
PDF_CARD_H = 145
PDF_GRID_COLS = 4
PDF_GRID_ROWS = 4
PDF_MARGIN = 5
PDF_FONT = "Helvetica"
PDF_FONT_SIZE = 15
PDF_NAME_PAD = 20
PDF_NAME_BELOW = 12
PDF_HEADER_SIZE = 45
PDF_HEADER_PAD = 145
PDF_PAGE_NUM_FONT_SIZE = 22
PDF_HEADER_X = 10
PDF_HEADER_Y = 750
PDF_CARD_SPACING_X = 15
PDF_CARD_SPACING_Y = 22
PDF_TEXT_OFFSET_X = 0
PDF_TEXT_OFFSET_Y = -2

CARDS_LIST_TITLE = "CARDS LIST"
CARDS_LIST_CARD_W = 160
CARDS_LIST_CARD_H = 200
CARDS_LIST_GRID_COLS = 3
CARDS_LIST_GRID_ROWS = 3
CARDS_LIST_MARGIN = 28
CARDS_LIST_FONT = "Helvetica"
CARDS_LIST_FONT_SIZE = 20
CARDS_LIST_NAME_PAD = 18
CARDS_LIST_NAME_BELOW = 15
CARDS_LIST_HEADER_SIZE = 23
CARDS_LIST_HEADER_PAD = 185
CARDS_LIST_HEADER_X = 229
CARDS_LIST_HEADER_Y = 770
CARDS_LIST_CARD_SPACING_X = 30
CARDS_LIST_CARD_SPACING_Y = 32
CARDS_LIST_TEXT_OFFSET_X = 0
CARDS_LIST_TEXT_OFFSET_Y = -11

SHOW_CARDS_LIST_DEFAULT = True

BOARD_SIZE = PDF_GRID_COLS * PDF_GRID_ROWS

def wrap_text(canvas, text, max_width, font_name, font_size):
    canvas.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        width = canvas.stringWidth(test_line, font_name, font_size)
        
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                lines.append(word)
    
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [text]

def draw_wrapped_text(canvas, text, x, y, max_width, font_name, font_size, line_height=None):
    if line_height is None:
        line_height = font_size * 1.2
    
    lines = wrap_text(canvas, text, max_width, font_name, font_size)
    total_height = len(lines) * line_height
    
    start_y = y + total_height / 2 - line_height / 2
    
    for i, line in enumerate(lines):
        line_y = start_y - i * line_height
        canvas.setFont(font_name, font_size)
        canvas.drawCentredString(x, line_y, line)

class ScrollableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        canvas = tk.Canvas(self, borderwidth=0, height=900)
        vscroll = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

class Card:
    def __init__(self, idx, name=None, image=None):
        self.idx = idx
        self.name = name or f"Card {idx+1}"
        self.orig_image = image or Image.new("RGBA", (MAIN_CARD_W, MAIN_CARD_H-40), (200,200,200,255))
        self.zoom = 1.0
        self.offset = (0, 0)
        self.update_display_image()

    def get_display_image(self):
        w, h = self.orig_image.size
        zw, zh = int(w*self.zoom), int(h*self.zoom)
        img = self.orig_image.resize((zw, zh), Image.LANCZOS)
        cx, cy = zw//2, zh//2
        ox, oy = self.offset
        left = max(0, cx - MAIN_CARD_W//2 + ox)
        upper = max(0, cy - (MAIN_CARD_H-40)//2 + oy)
        right = left + MAIN_CARD_W
        lower = upper + (MAIN_CARD_H-40)
        if right > zw:
            right = zw
            left = right - MAIN_CARD_W
        if lower > zh:
            lower = zh
            upper = lower - (MAIN_CARD_H-40)
        box = (left, upper, right, lower)
        cropped = img.crop(box)
        return cropped

    def update_display_image(self):
        disp = self.get_display_image()
        self.image = disp
        self.tkimg = ImageTk.PhotoImage(disp)

    def set_image(self, img):
        self.orig_image = img.resize((MAIN_CARD_W, MAIN_CARD_H-40), Image.LANCZOS)
        self.zoom = 1.0
        self.offset = (0, 0)
        self.update_display_image()

class ImageEditor(tk.Toplevel):
    def __init__(self, parent, card, on_save):
        super().__init__(parent)
        self.title("Edit Image - Zoom & Pan")
        self.attributes("-topmost", True)
        self.card = card
        self.on_save = on_save
        self.canvas = tk.Canvas(self, width=MAIN_CARD_W, height=MAIN_CARD_H-40, bg='grey')
        self.canvas.pack()
        self.zoom_slider = tk.Scale(self, from_=0.1, to=3.0, resolution=0.05,
                                    orient=tk.HORIZONTAL, label="Zoom", command=self.on_zoom)
        self.zoom_slider.set(self.card.zoom)
        self.zoom_slider.pack(fill=tk.X, padx=10)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Load New Image", command=self.load_new_image).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save", command=self.save_and_close).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        self.img_on_canvas = None
        self.drag_data = {"x": 0, "y": 0}
        self.redraw_image()
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)

    def load_new_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA")
            self.card.orig_image = img
            self.card.zoom = 1.0
            self.card.offset = (0, 0)
            self.zoom_slider.set(1.0)
            self.redraw_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def redraw_image(self):
        self.card.update_display_image()
        self.card.tkimg = ImageTk.PhotoImage(self.card.get_display_image())
        if self.img_on_canvas is None:
            self.img_on_canvas = self.canvas.create_image(MAIN_CARD_W//2, (MAIN_CARD_H-40)//2, image=self.card.tkimg)
        else:
            self.canvas.itemconfigure(self.img_on_canvas, image=self.card.tkimg)

    def on_zoom(self, val):
        self.card.zoom = float(val)
        self.redraw_image()

    def on_drag_start(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_move(self, event):
        dx = -(event.x - self.drag_data["x"])
        dy = -(event.y - self.drag_data["y"])
        ox, oy = self.card.offset
        self.card.offset = (ox + dx, oy + dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.redraw_image()

    def save_and_close(self):
        self.on_save()
        self.destroy()

class LoteriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lotería Board Generator")
        self.cards = [Card(i) for i in range(54)]
        self.include_cards_list = tk.BooleanVar(value=SHOW_CARDS_LIST_DEFAULT)
        self.make_ui()
        self.draw_cards()

    def make_ui(self):
        top = tk.Frame(self.root); top.pack(pady=5)
        tk.Label(top, text="Boards:", font=("Arial", 16)).pack(side=tk.LEFT)
        self.nboards = tk.Entry(top, width=3, font=("Arial", 16)); self.nboards.insert(0,"1"); self.nboards.pack(side=tk.LEFT)
        tk.Button(top, text="Export PDF", font=("Arial", 14), command=self.export_pdf).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(top, text="Include Cards List", font=("Arial", 14), variable=self.include_cards_list).pack(side=tk.LEFT, padx=10)
        self.scroll_frame = ScrollableFrame(self.root)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.cards_frame = self.scroll_frame.scrollable_frame

    def draw_cards(self):
        for w in self.cards_frame.winfo_children(): w.destroy()
        for i, card in enumerate(self.cards):
            row, col = divmod(i, MAIN_GRID_COLS)
            f = tk.Frame(self.cards_frame, width=MAIN_CARD_W, height=MAIN_CARD_H, bd=1, relief=tk.RAISED)
            f.grid(row=row, column=col, padx=MAIN_GRID_PADX, pady=MAIN_GRID_PADY)
            img_lbl = tk.Label(f, image=card.tkimg, cursor="hand2"); img_lbl.pack()
            img_lbl.bind("<Button-1>", lambda e, c=card: self.open_image_editor(c))
            name_lbl = tk.Label(f, text=card.name, font=MAIN_FONT, wraplength=MAIN_CARD_W-8)
            name_lbl.pack(fill=tk.X, pady=(10,0))
            name_lbl.bind("<Button-1>", lambda e, c=card, l=name_lbl: self.edit_name(c, l))

    def edit_name(self, card, label):
        win = tk.Toplevel(self.root); win.title("Edit Name")
        e = tk.Entry(win, font=MAIN_FONT); e.pack(padx=10,pady=10); e.insert(0,card.name); e.focus()
        def save():
            card.name = e.get(); label.config(text=card.name); win.destroy()
        tk.Button(win, text="OK", font=MAIN_FONT, command=save).pack(pady=5)

    def open_image_editor(self, card):
        def on_save():
            card.update_display_image()
            self.draw_cards()
        editor = ImageEditor(self.root, card, on_save)
        editor.grab_set()

    def export_pdf(self):
        try: n = max(1, int(self.nboards.get()))
        except: messagebox.showerror("Error","Invalid number of boards"); return
        boards = [random.sample(self.cards, BOARD_SIZE) for _ in range(n)]
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not path: return
        c = canvas.Canvas(path, pagesize=letter)
        pw, ph = letter
        for bidx, board in enumerate(boards):
            c.setFont(PDF_FONT, PDF_HEADER_SIZE)
            c.drawString(PDF_HEADER_X, PDF_HEADER_Y, str(bidx+1))
            cols, rows = PDF_GRID_COLS, PDF_GRID_ROWS
            total_w = cols * (PDF_CARD_W + PDF_CARD_SPACING_X) - PDF_CARD_SPACING_X
            x_off = (pw - total_w) / 2
            y_start = ph - PDF_MARGIN - PDF_HEADER_SIZE - PDF_HEADER_PAD
            for i, card in enumerate(board):
                col = i % cols
                row = i // cols
                x = x_off + col * (PDF_CARD_W + PDF_CARD_SPACING_X)
                y = y_start - row * (PDF_CARD_H + PDF_CARD_SPACING_Y + PDF_FONT_SIZE)
                img_bytes = io.BytesIO(); card.image.resize((PDF_CARD_W, PDF_CARD_H), Image.LANCZOS).save(img_bytes, format='PNG'); img_bytes.seek(0)
                c.drawImage(ImageReader(img_bytes), x, y, width=PDF_CARD_W, height=PDF_CARD_H)
                c.setFont(PDF_FONT, PDF_FONT_SIZE)
                text_x = x + PDF_CARD_W/2 + PDF_TEXT_OFFSET_X
                text_y = y - PDF_NAME_PAD + PDF_TEXT_OFFSET_Y
                draw_wrapped_text(c, card.name[:30], text_x, text_y, PDF_CARD_W, PDF_FONT, PDF_FONT_SIZE)
            c.showPage()
        if self.include_cards_list.get():
            per_page = CARDS_LIST_GRID_COLS * CARDS_LIST_GRID_ROWS
            for page in range((len(self.cards)+per_page-1)//per_page):
                c.setFont(CARDS_LIST_FONT, CARDS_LIST_HEADER_SIZE)
                c.drawString(CARDS_LIST_HEADER_X, CARDS_LIST_HEADER_Y, CARDS_LIST_TITLE)
                cols, rows = CARDS_LIST_GRID_COLS, CARDS_LIST_GRID_ROWS
                total_w = cols * (CARDS_LIST_CARD_W + CARDS_LIST_CARD_SPACING_X) - CARDS_LIST_CARD_SPACING_X
                x_off = (pw - total_w) / 2
                y_start = ph - CARDS_LIST_MARGIN - CARDS_LIST_HEADER_SIZE - CARDS_LIST_HEADER_PAD
                for idx in range(per_page):
                    card_idx = page*per_page+idx
                    if card_idx >= len(self.cards): break
                    card = self.cards[card_idx]
                    col = idx % cols
                    row = idx // cols
                    x = x_off + col * (CARDS_LIST_CARD_W + CARDS_LIST_CARD_SPACING_X)
                    y = y_start - row * (CARDS_LIST_CARD_H + CARDS_LIST_CARD_SPACING_Y + CARDS_LIST_FONT_SIZE)
                    img_bytes = io.BytesIO(); card.image.resize((CARDS_LIST_CARD_W, CARDS_LIST_CARD_H), Image.LANCZOS).save(img_bytes, format='PNG'); img_bytes.seek(0)
                    c.drawImage(ImageReader(img_bytes), x, y, width=CARDS_LIST_CARD_W, height=CARDS_LIST_CARD_H)
                    c.setFont(CARDS_LIST_FONT, CARDS_LIST_FONT_SIZE)
                    text_x = x + CARDS_LIST_CARD_W/2 + CARDS_LIST_TEXT_OFFSET_X
                    text_y = y - CARDS_LIST_NAME_PAD + CARDS_LIST_TEXT_OFFSET_Y
                    draw_wrapped_text(c, card.name[:30], text_x, text_y, CARDS_LIST_CARD_W, CARDS_LIST_FONT, CARDS_LIST_FONT_SIZE)
                c.showPage()
        c.save()
        messagebox.showinfo("Done", f"PDF saved: {os.path.basename(path)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1300x1000")
    app = LoteriaApp(root)
    root.mainloop() 