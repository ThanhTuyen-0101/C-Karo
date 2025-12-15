# main.py
from gui.caro_gui import CaroGUI
from game.board import CaroBoard
from ai.ai_caro import CaroAI  # Import đúng class và tên file

if __name__ == "__main__":
    board = CaroBoard()        
    ai = CaroAI()              
    game = CaroGUI(board_size=15, board=board, ai=ai)
    game.run()