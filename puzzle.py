import requests
import json
import tkinter

class Puzzle:
    def __init__(self, fen, moves):
        self.fen = fen
        self.moves = moves


def get_puzzle_json(rating: int | None = None, themes: list | None = None):
    URL = "https://chess-puzzles.p.rapidapi.com/"
    querystring = {}
    if rating:
        querystring["rating"] = rating
    if themes:
        querystring["themes"] = "[\"" + "\",\"".join(themes) + "\"]"  # string in form '["middlegame","advantage"]'
        querystring["themesType"] = "ALL"
    headers = {
	"X-RapidAPI-Key": "53615e0c4fmsh48be14a9b648a42p1c1f4ejsn168f25fb17c3",
	"X-RapidAPI-Host": "chess-puzzles.p.rapidapi.com"
    }
    response = requests.get(URL, headers=headers, params=querystring)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return None
    return response.json()

if __name__ == "__main__":
    with open("test_puzzle.json", "w") as f:
        json.dump(get_puzzle_json(), f)