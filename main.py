# main.py
from gui.caro_gui import CaroGUI
from game.board import CaroBoard
from ai.minimax import find_best_move, X, O, EMPTY   # nếu cần

if __name__ == "__main__":
    app = CaroGUI()
    app.run()
