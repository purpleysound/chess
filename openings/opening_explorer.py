import tkinter as tk
import json

with open("openings/eco.json", "r") as f:
    openings = json.load(f)

name_FEN_index_triplets = [[opening["eco"]+": "+opening["name"], opening["fen"], i] for i, opening in enumerate(openings)]
name_FEN_index_triplets.sort()
FENs = set([opening[1] for opening in name_FEN_index_triplets])

def _update_searchbox(data: list, suggested):
    suggested.delete(0, tk.END)
    for item in data:
        suggested.insert(tk.END, item)

def _delay_label(event, chosen_display, suggested, chosen_opening, window):
    window.after(100, lambda: _update_label(chosen_display, suggested, chosen_opening))

def _update_label(chosen_display, suggested, chosen_opening):
    chosen_opening.set(suggested.get(tk.ACTIVE))
    chosen_display["text"] = chosen_opening.get()

def _check(event, search_box, suggested):
    text = search_box.get()
    if not text:
        data = [opening[0] for opening in name_FEN_index_triplets]
    else:
        data = []
        for item in [opening[0] for opening in name_FEN_index_triplets]:
            if "".join(letter for letter in text.lower() if letter in "abcdefghijklmnopqrstuvwxyz0123456789") in "".join(letter for letter in item.lower() if letter in "abcdefghijklmnopqrstuvwxyz0123456789"):
                data.append(item)
    _update_searchbox(data, suggested)

def _return_opening(opening, window):
    global FEN_to_return
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
    top_label = tk.Label(window, text="Chosen Opening:")
    top_label.pack(pady=10)
    chosen_display = tk.Label(window, text=chosen_opening.get(), font=("Segoe UI",15))
    chosen_display.pack()
    return_button = tk.Button(text="Confirm", command=lambda: _return_opening(chosen_opening.get(), window))
    return_button.pack(pady=10)
    search_label = tk.Label(text="Search:")
    search_label.pack()
    search_box = tk.Entry(window, width=50)
    search_box.pack(pady=10)
    suggested = tk.Listbox(window, width=100)
    suggested.pack()
    _update_searchbox([opening[0] for opening in name_FEN_index_triplets], suggested)
    suggested.bind("<<ListboxSelect>>", lambda x: _delay_label(x, chosen_display, suggested, chosen_opening, window))
    search_box.bind("<KeyRelease>", lambda x: _check(x, search_box, suggested))
    window.mainloop()
    return FEN_to_return

FEN_to_return = ""

if __name__ == "__main__":
    open_window()