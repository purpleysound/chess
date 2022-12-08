import tkinter as tk
import json
from functools import partial

with open("openings/eco.json", "r") as f:
    openings = json.load(f)

name_FEN_index_triplets = [[opening["eco"]+": "+opening["name"], opening["fen"], i] for i, opening in enumerate(openings)]
name_FEN_index_triplets.sort()

def open_window():
    window = tk.Tk()
    window.wm_title("Opening Explorer")

    chosen_opening = tk.StringVar(window)
    chosen_opening.set("B00: King's Pawn")
    drop_down = tk.OptionMenu(window, chosen_opening, *[opening[0] for opening in name_FEN_index_triplets])
    drop_down.pack()
    return_button = tk.Button(text="Confirm", command=partial(eval, "return chosen_opening.get()")) #idk how to return something back to the main program
    return_button.pack()
    window.mainloop()

if __name__ == "__main__":
    open_window()