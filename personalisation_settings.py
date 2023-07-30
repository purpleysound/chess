from utils_and_constants import *
import pickle
import tkinter
import tkinter.filedialog
import PIL.Image
import PIL.ImageTk

class PersonalisationCustomiser:
    def __init__(self) -> None:
        self.root = tkinter.Tk()
        self.root.title("Personalisation Customiser")
        
        self.images = {}

    def run(self):
        # average tkinter program yippee!!
        background_colour_frame = tkinter.Frame(self.root)
        background_colour_frame.grid(row=0, column=0)
        self.background_colour_getter = self.make_colour_picker(background_colour_frame, "Background Colour")
        secondary_colour_frame = tkinter.Frame(self.root)
        secondary_colour_frame.grid(row=0, column=1)
        self.secondary_colour_getter = self.make_colour_picker(secondary_colour_frame, "Secondary Colour")
        move_colour_frame = tkinter.Frame(self.root)
        move_colour_frame.grid(row=0, column=2)
        self.move_colour_getter = self.make_colour_picker(move_colour_frame, "Move Colour")
        engine_depth_frame = tkinter.Frame(self.root)
        engine_depth_frame.grid(row=1, column=0)
        engine_depth_label = tkinter.Label(engine_depth_frame, text="Engine Depth")
        engine_depth_label.pack()
        engine_depth_entry = tkinter.Entry(engine_depth_frame)
        engine_depth_entry.pack()
        self.engine_depth_getter = lambda: int(engine_depth_entry.get())  # normally this is not conventional, but i believe i have good reason to do so
        font_size_frame = tkinter.Frame(self.root)
        font_size_frame.grid(row=1, column=1)
        font_size_label = tkinter.Label(font_size_frame, text="Font Size")
        font_size_label.pack()
        font_size_entry = tkinter.Entry(font_size_frame)
        font_size_entry.pack()
        self.font_size_getter = lambda: int(font_size_entry.get())
        min_engine_time_frame = tkinter.Frame(self.root)
        min_engine_time_frame.grid(row=1, column=2)
        min_engine_time_label = tkinter.Label(min_engine_time_frame, text="Min Engine Time (Seconds)")
        min_engine_time_label.pack()
        min_engine_time_entry = tkinter.Entry(min_engine_time_frame)
        min_engine_time_entry.pack()
        self.min_engine_time_getter = lambda: int(min_engine_time_entry.get())

        piece_images_frame = tkinter.Frame(self.root)
        piece_images_frame.grid(row=2, column=0, columnspan=3)
        white_piece_images_frame = tkinter.Frame(piece_images_frame)
        white_piece_images_frame.grid(row=0, column=0)
        black_piece_images_frame = tkinter.Frame(piece_images_frame)
        black_piece_images_frame.grid(row=1, column=0)
        PIECE_NAMES = ["Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]
        for piece in range(6):
            white_piece_image_frame = tkinter.Frame(white_piece_images_frame)
            white_piece_image_frame.grid(row=0, column=piece)
            white_piece_image_label = tkinter.Label(white_piece_image_frame, text=PIECE_NAMES[piece])
            white_piece_image_label.pack()
            self.make_image_uploader(white_piece_image_frame, f"White {PIECE_NAMES[piece]}", piece+8)
            black_piece_image_frame = tkinter.Frame(black_piece_images_frame)
            black_piece_image_frame.grid(row=1, column=piece)
            black_piece_image_label = tkinter.Label(black_piece_image_frame, text=PIECE_NAMES[piece])
            black_piece_image_label.pack()
            self.make_image_uploader(black_piece_image_frame, f"Black {PIECE_NAMES[piece]}", piece)

        finish_buttons_frame = tkinter.Frame(self.root)
        finish_buttons_frame.grid(row=3, column=0, columnspan=3)
        submit_button = tkinter.Button(finish_buttons_frame, text="Submit (invalid inputs will not be changed)", command=self.submit)
        submit_button.grid(row=0, column=0)
        reset_button = tkinter.Button(finish_buttons_frame, text="Reset to Defaults", command=self.reset)
        reset_button.grid(row=0, column=1)
        self.root.mainloop()

    def reset(self):
        with open("default_preferences.pkl", "rb") as f:
            pref = pickle.load(f)
        with open("preferences.pkl", "wb") as f:
            pickle.dump(pref, f)
        print("Please restart the program for changes to take effect.")
        self.root.destroy()

    def submit(self):
        with open("preferences.pkl", "rb") as f:
            pref = pickle.load(f)
        key_getter_pairs = [
            (Prefs.BACKGROUND_COLOUR, self.background_colour_getter),
            (Prefs.CONTRASTING_COLOUR, self.secondary_colour_getter),
            (Prefs.MOVE_INDICATOR_COLOUR, self.move_colour_getter),
            (Prefs.DEFAULT_ENGINE_DEPTH, self.engine_depth_getter),
            (Prefs.FONT_SIZE, self.font_size_getter),
            (Prefs.MINIMUM_ENGINE_TIME, self.min_engine_time_getter),
        ]
        for key, getter in key_getter_pairs:
            try:
                pref[key] = getter()
            except ValueError:
                pass
        for key, image in self.images.items():
            if image:
                pref[Prefs.PIECE_IMAGES][key] = image
        with open("preferences.pkl", "wb") as f:
            pickle.dump(pref, f)
        print("Please restart the program for changes to take effect.")
        self.root.destroy()

    def make_image_uploader(self, frame, text, piece: int):
        label = tkinter.Label(frame, text=text)
        label.pack()
        image_button = tkinter.Button(frame, width=64, height=64, image=tkinter.PhotoImage(file="images/transparent.png"))
        image_button.pack()
        browse_button = tkinter.Button(frame, text="Browse", command=lambda: self.browse_image(image_button, piece))
        browse_button.pack(side=tkinter.BOTTOM)

    def browse_image(self, image_button: tkinter.Button, key: int):
        f_types = [("PNG", "*.png"), ("JPEG", "*.jpg"), ("SVG", "*.svg")]
        image_path = tkinter.filedialog.askopenfilename(filetypes=f_types)
        if image_path:
            self.images[key] = image_path
            image = PIL.Image.open(image_path)
            image = image.resize((64, 64))
            image = PIL.ImageTk.PhotoImage(image)
            image_button.configure(image=image._PhotoImage__photo)

    def make_colour_picker(self, frame, text):
        """Returns a getter function for the rgb tuple, values unvalidated"""
        label = tkinter.Label(frame, text=text)
        label.pack()
        rgb_frame = tkinter.Frame(frame)
        rgb_frame.pack()
        r_label = tkinter.Label(rgb_frame, text="R")
        r_label.grid(row=0, column=0)
        r_entry = tkinter.Entry(rgb_frame)
        r_entry.grid(row=0, column=1)
        g_label = tkinter.Label(rgb_frame, text="G")
        g_label.grid(row=1, column=0)
        g_entry = tkinter.Entry(rgb_frame)
        g_entry.grid(row=1, column=1)
        b_label = tkinter.Label(rgb_frame, text="B")
        b_label.grid(row=2, column=0)
        b_entry = tkinter.Entry(rgb_frame)
        b_entry.grid(row=2, column=1)
        colour_preview = tkinter.Canvas(rgb_frame, width=50, height=50)
        colour_preview.grid(row=3, column=0, columnspan=2)
        r_entry.bind("<KeyRelease>", lambda e: self.update_colour_preview(r_entry.get(), g_entry.get(), b_entry.get(), colour_preview))
        g_entry.bind("<KeyRelease>", lambda e: self.update_colour_preview(r_entry.get(), g_entry.get(), b_entry.get(), colour_preview))
        b_entry.bind("<KeyRelease>", lambda e: self.update_colour_preview(r_entry.get(), g_entry.get(), b_entry.get(), colour_preview))
        return lambda: (int(r_entry.get()), int(g_entry.get()), int(b_entry.get()))

    def update_colour_preview(self, r, g, b, canvas: tkinter.Canvas):
        if any([not i.isdigit() for i in (r, g, b)]):
            return
        if any([not int(i) in range(256) for i in (r, g, b)]):
            return
        canvas.create_rectangle(0, 0, 50, 50, fill=f"#{dth(r)}{dth(g)}{dth(b)}")

 
def dth(num: str) -> str:
    """Converts a decimal number to a hexadecimal number"""""
    string = hex(int(num))[2:].upper()
    if len(string) == 1:
        return "0" + string
    return string


def open_window():
    PersonalisationCustomiser().run()


if __name__ == "__main__":
    open_window()
