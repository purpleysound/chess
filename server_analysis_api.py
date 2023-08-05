from flask import Flask, request, jsonify
from utils_and_constants import *
import engine
import game

app = Flask(__name__)

@app.route("/chess/<fen>")
def get_analysis(fen):
    fen = fen.replace("=", "/")
    d = request.args.get("d")
    if d:
        depth = int(d)
    else:
        depth = 4
    return jsonify(engine.get_value_and_best_move(game.Game(fen), depth)), 200

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)