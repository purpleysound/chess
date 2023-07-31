import tkinter
import piece
import random
import game

class ScenarioCreator:
    def __init__(self) -> None:
        self.root = tkinter.Tk()
        self.root.title("Scenario Creator")
        self.fen = None

    def run(self):
        info_label = tkinter.Label(self.root, text="Scenario Creator")
        info_label.pack()
        pieces_frame = tkinter.Frame(self.root)
        pieces_frame.pack()
        pieces = ["Pawn", "Knight", "Bishop", "Rook", "Queen"]
        colours = ["White", "Black"]
        self.num_boxes = {}
        for i, piece_type in enumerate(pieces):
            for j, colour in enumerate(colours):
                piece_label = tkinter.Label(pieces_frame, text=f"{colour} {piece_type}", padx=5, pady=5)
                piece_label.grid(row=2*j, column=i)
                piece_num_box = tkinter.Spinbox(pieces_frame, from_=0, to=8, width=3)
                piece_num_box.grid(row=2*j+1, column=i)
                generated_piece = piece.generate_piece(i, not j)
                self.num_boxes[generated_piece] = piece_num_box

        black_or_white_frame = tkinter.Frame(self.root)
        black_or_white_frame.pack()
        b_or_w_label = tkinter.Label(black_or_white_frame, text="Leave ticked for white to move, untick for black to move", padx=5, pady=5)
        b_or_w_label.grid(row=0, column=0)
        self.white = tkinter.BooleanVar(value=True)
        b_or_w_checkbutton = tkinter.Checkbutton(black_or_white_frame, variable=self.white)
        b_or_w_checkbutton.grid(row=0, column=1)

        self.confirm_button = tkinter.Button(self.root, text="Confirm", command=self.generate_good_fen)
        self.confirm_button.pack()

        self.root.mainloop()

    def generate_good_fen(self):
        while True:
            self.generate_fen()
            if self.fen is None:
                return
            g = game.Game(self.fen)
            g.white_move = not g.white_move
            if g.in_check():  # im probably being stupid but i swear it should be not g.in_check() but that gives the opposite result
                g.white_move = not g.white_move
                if g.in_check():
                    self.root.destroy()
                    return

    def generate_fen(self):
        long_board = []
        for piece_type, num_box in self.num_boxes.items():
            try:
                count = int(num_box.get())
            except TypeError:
                self.confirm_button.config(text="Invalid number")
                return
            for _ in range(count):
                long_board.append(piece_type)
        long_board.append(5)  # kings
        long_board.append(13)

        total_piece_count = len(long_board)
        if total_piece_count > 24:
            self.confirm_button.config(text="Too many pieces!")
            return
        else:
            for _ in range(64 - total_piece_count):
                long_board.append(None)
        long_board = better_shuffle(long_board)
        board = []
        for i in range(8):
            board.append(long_board[i*8:(i+1)*8])

        piece_to_letter = {piece.PAWN: "p", piece.KNIGHT: "n", piece.BISHOP: "b", piece.ROOK: "r", piece.QUEEN: "q", piece.KING: "k"}
        fen = ""
        blank_count = 0
        for rank in board[::-1]:
            for item in rank:
                if item is None:
                    blank_count += 1
                else:
                    if blank_count > 0:
                        fen += str(blank_count)
                        blank_count = 0
                    piece_type, white = piece.get_piece_attrs(item)
                    fen += piece_to_letter[piece_type].upper() if white else piece_to_letter[piece_type]
            if blank_count > 0:
                fen += str(blank_count)
                blank_count = 0
            fen += "/"
        fen = fen[:-1]  # remove last slash
        fen += " w " if self.white.get() else " b "
        fen += "-"
        self.fen = fen


def better_shuffle(l: list[int | None]):
    """Shuffles without leaving pawns 1 move away from promotion"""
    l = l.copy()
    for i, item in enumerate(l):
        if item is not None and piece.get_piece_type(item) == piece.PAWN:
            while True:
                j = random.randint(16, 49)
                if l[j] is None or piece.get_piece_type(l[j]) != piece.PAWN: # type: ignore (these arent none bc i just checked but pylance is silly)
                    break
        else:
            while True:
                j = random.randint(0, 63)
                if l[j] is None or piece.get_piece_type(l[j]) != piece.PAWN: # type: ignore
                    break
        l[i], l[j] = l[j], l[i]
    return l


def main():
    s = ScenarioCreator()
    s.run()
    return s.fen


if __name__ == "__main__":
    print(main())