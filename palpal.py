import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import sys
import os
from tkinter.filedialog import askopenfilename

# ── resource helper ────────────────────────────────────────────────────────────
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ── palette ────────────────────────────────────────────────────────────────────
BG          = "#0d0f12"
PANEL       = "#13161b"
BORDER      = "#1e2530"
ACCENT      = "#00e5ff"
ACCENT_DIM  = "#007a8a"
TEXT        = "#c8d6e5"
TEXT_DIM    = "#4a5568"
TEXT_BRIGHT = "#ffffff"
SUCCESS     = "#00ff9d"
ERROR       = "#ff4d6a"

# ── state ──────────────────────────────────────────────────────────────────────
img_path    = ""
output_text = ""

# ── pixel normalisation ────────────────────────────────────────────────────────
def normalise_pixel(value, mode):
    if isinstance(value, int):
        return [value]
    if isinstance(value, float):
        return [max(0, min(255, int(value)))]
    return list(value)

# ── core logic ─────────────────────────────────────────────────────────────────
def get_arr():
    global output_text
    if not img_path:
        set_status("No file selected — choose an image first.", kind="error")
        return

    set_status("Processing…", kind="info")
    root.update()

    try:
        im = Image.open(img_path)
    except Exception as e:
        set_status(f"Could not open image: {e}", kind="error")
        return

    if im.mode == "P":
        im = im.convert("RGB")
    elif im.mode == "1":
        im = im.convert("L")

    pix = im.load()
    width, height = im.size

    rows = []
    for i in range(height):
        cells = []
        for j in range(width):
            bytes_ = normalise_pixel(pix[j, i], im.mode)
            cells.append(",".join(str(b) for b in bytes_))
        rows.append("db " + ", ".join(cells))

    output_text = "\n".join(rows)

    text_widget.config(state=tk.NORMAL, fg=SUCCESS)
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, output_text)
    text_widget.config(state=tk.DISABLED)

    mode_label.config(text=f"mode:{im.mode}  {width}×{height}px  {len(rows)} rows")
    set_status(f"Done — {len(rows)} rows generated.", kind="ok")


def copy():
    if not output_text:
        set_status("Nothing to copy yet.", kind="error")
        return
    root.clipboard_clear()
    root.clipboard_append(output_text)
    root.update()
    set_status("Copied to clipboard ✓", kind="ok")


def getPath():
    global img_path
    filename = askopenfilename(
        title="Open image file",
        filetypes=[
            ("Image files",
             "*.bmp *.png *.jpg *.jpeg *.gif *.tiff *.tif "
             "*.webp *.ico *.ppm *.pgm *.pbm *.pnm "
             "*.tga *.pcx *.xbm *.xpm *.dds *.hdr *.exr"),
            ("All files", "*.*"),
        ]
    )
    if filename:
        img_path = filename
        short = os.path.basename(filename)
        file_label.config(text=short, fg=ACCENT)
        mode_label.config(text="")
        set_status(f"Loaded: {short}", kind="ok")
        text_widget.config(state=tk.NORMAL, fg=TEXT_DIM)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END,
            "; file loaded — click [ CONVERT ] to generate output\n")
        text_widget.config(state=tk.DISABLED)


def set_status(msg, kind="info"):
    colours = {"info": TEXT_DIM, "ok": SUCCESS, "error": ERROR}
    status_label.config(text=msg, fg=colours.get(kind, TEXT_DIM))


# ── window ─────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("PalPal")
root.configure(bg=BG)
root.geometry("860x620")
root.minsize(680, 480)

icon_path = resource_path(os.path.join("imgs", "walrusformin.png"))
if os.path.exists(icon_path):
    try:
        root.iconphoto(True, tk.PhotoImage(file=icon_path))
    except Exception:
        pass

# ── header ─────────────────────────────────────────────────────────────────────
header = tk.Frame(root, bg=PANEL, height=56)
header.pack(fill=tk.X, side=tk.TOP)
header.pack_propagate(False)

tk.Frame(header, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)

tk.Label(header, text="PALPAL", bg=PANEL, fg=ACCENT,
         font=("Courier", 22, "bold"), padx=18).pack(side=tk.LEFT)

# ── toolbar divider ────────────────────────────────────────────────────────────
tk.Frame(root, bg=BORDER, height=1).pack(fill=tk.X)

# ── controls ───────────────────────────────────────────────────────────────────
controls = tk.Frame(root, bg=BG, pady=14, padx=20)
controls.pack(fill=tk.X)

def make_btn(parent, text, cmd, primary=False):
    bg_default = ACCENT if primary else BORDER
    fg_default = BG if primary else TEXT
    bg_hover   = ACCENT_DIM if primary else "#252d3a"
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg_default, fg=fg_default,
        activebackground=bg_hover, activeforeground=fg_default,
        font=("Courier", 12, "bold"),
        relief=tk.FLAT, bd=0,
        padx=18, pady=9, cursor="hand2"
    )
    b.bind("<Enter>", lambda e: b.config(bg=bg_hover))
    b.bind("<Leave>", lambda e: b.config(bg=bg_default))
    return b

btn_open    = make_btn(controls, "[ OPEN FILE ]",   getPath, primary=True)
btn_convert = make_btn(controls, "[ CONVERT ]",     get_arr)
btn_copy    = make_btn(controls, "[ COPY ]",        copy)

btn_open.pack(side=tk.LEFT, padx=(0, 8))
btn_convert.pack(side=tk.LEFT, padx=(0, 8))
btn_copy.pack(side=tk.LEFT)

info_frame = tk.Frame(controls, bg=BG)
info_frame.pack(side=tk.RIGHT)

file_label = tk.Label(info_frame, text="no file selected",
                       bg=BG, fg=TEXT_DIM, font=("Courier", 11), anchor="e")
file_label.pack(anchor="e")

mode_label = tk.Label(info_frame, text="",
                       bg=BG, fg=TEXT_DIM, font=("Courier", 10), anchor="e")
mode_label.pack(anchor="e")

# ── divider ────────────────────────────────────────────────────────────────────
tk.Frame(root, bg=BORDER, height=1).pack(fill=tk.X)

# ── output ─────────────────────────────────────────────────────────────────────
output_frame = tk.Frame(root, bg=BG, padx=20, pady=12)
output_frame.pack(fill=tk.BOTH, expand=True)

label_row = tk.Frame(output_frame, bg=BG)
label_row.pack(fill=tk.X, pady=(0, 8))

tk.Label(label_row, text="OUTPUT", bg=BG, fg=ACCENT,
         font=("Courier", 10, "bold")).pack(side=tk.LEFT)
tk.Label(label_row, text=" ── assembly db format",
         bg=BG, fg=TEXT_DIM, font=("Courier", 10)).pack(side=tk.LEFT)

# bordered text box
text_outer = tk.Frame(output_frame, bg=BORDER, padx=1, pady=1)
text_outer.pack(fill=tk.BOTH, expand=True)

text_inner = tk.Frame(text_outer, bg=PANEL)
text_inner.pack(fill=tk.BOTH, expand=True)

scrollbar_y = tk.Scrollbar(text_inner, bg=BORDER, troughcolor=BG,
                            relief=tk.FLAT, bd=0, width=10)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

scrollbar_x = tk.Scrollbar(text_inner, orient=tk.HORIZONTAL,
                            bg=BORDER, troughcolor=BG,
                            relief=tk.FLAT, bd=0, width=10)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

text_widget = tk.Text(
    text_inner,
    bg=PANEL, fg=TEXT_DIM,
    font=("Courier", 11),
    relief=tk.FLAT, bd=0,
    insertbackground=ACCENT,
    selectbackground=ACCENT_DIM,
    selectforeground=BG,
    wrap=tk.NONE,
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    state=tk.DISABLED,
    padx=14, pady=12,
)
text_widget.pack(fill=tk.BOTH, expand=True)
scrollbar_y.config(command=text_widget.yview)
scrollbar_x.config(command=text_widget.xview)

# placeholder
text_widget.config(state=tk.NORMAL)
text_widget.insert(tk.END,
    "; open an image and click [ CONVERT ] to generate assembly db output\n"
    ";\n"
    "; each row corresponds to one scanline:\n"
    ";   db R,G,B, R,G,B, …   (channels depend on image colour mode)\n"
)
text_widget.config(state=tk.DISABLED)

# ── status bar ─────────────────────────────────────────────────────────────────
tk.Frame(root, bg=BORDER, height=1).pack(fill=tk.X)

status_bar = tk.Frame(root, bg=PANEL, height=26)
status_bar.pack(fill=tk.X, side=tk.BOTTOM)
status_bar.pack_propagate(False)

tk.Label(status_bar, text="●", bg=PANEL, fg=ACCENT,
         font=("Courier", 9), padx=10).pack(side=tk.LEFT)

status_label = tk.Label(status_bar, text="ready",
                         bg=PANEL, fg=TEXT_DIM,
                         font=("Courier", 10), anchor="w")
status_label.pack(side=tk.LEFT)

tk.Label(status_bar, text="PalPal",
         bg=PANEL, fg=TEXT_DIM,
         font=("Courier", 10), padx=12).pack(side=tk.RIGHT)

root.mainloop()
