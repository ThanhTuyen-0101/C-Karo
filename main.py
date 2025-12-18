import flet as ft
from gui.caro_gui import CaroGUI
from game.board import CaroBoard
from ai.minimax import CaroAI


# Hàm main của Flet bắt buộc phải nhận tham số 'page'
def main(page: ft.Page):
    # 1. Khởi tạo Luật chơi (Logic)
    my_board = CaroBoard()
   
    # 2. Khởi tạo Trí tuệ nhân tạo (AI)
    my_ai = CaroAI()


    # 3. Khởi tạo Giao diện (GUI)
    # Truyền biến 'page' vào class CaroGUI như yêu cầu
    app = CaroGUI(page, board_logic=my_board, ai_engine=my_ai)


if __name__ == "__main__":
    # Lệnh này sẽ tạo ra cửa sổ (page) và gọi hàm main
    ft.app(target=main)

