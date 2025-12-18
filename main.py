import flet as ft
from gui.caro_gui import CaroGUI
from game.board import CaroBoard
from ai.LogicAi import CaroAI

def main(page: ft.Page):
    my_board = CaroBoard()
    my_ai = CaroAI()
    app = CaroGUI(page, board_logic=my_board, ai_engine=my_ai)
if __name__ == "__main__":
    ft.app(target=main)

