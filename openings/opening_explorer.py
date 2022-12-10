import tkinter as tk
import json

with open("openings/eco.json", "r") as f:
    openings = json.load(f)

name_FEN_index_triplets = [[opening["eco"]+": "+opening["name"], opening["fen"], i] for i, opening in enumerate(openings)]
name_FEN_index_triplets.sort()

def return_opening(opening, window):
    global FEN_to_return
    print(opening)
    for triplet in name_FEN_index_triplets:
        if opening == triplet[0]:
            FEN_to_return = triplet[1]
            window.destroy()
            return

def open_window():
    window = tk.Tk()
    window.wm_title("Opening Explorer")

    chosen_opening = tk.StringVar(window)
    chosen_opening.set("B00: King's Pawn")
    drop_down = tk.OptionMenu(window, chosen_opening, *[opening[0] for opening in name_FEN_index_triplets])
    drop_down.pack()
    return_button = tk.Button(text="Confirm", command=lambda: return_opening(chosen_opening.get(), window)) #idk how to return something back to the main program
    return_button.pack()
    window.mainloop()
    return FEN_to_return

FEN_to_return = ""

if __name__ == "__main__":
    open_window()