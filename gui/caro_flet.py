import flet as ft
import sys
import os

# --- KẾT NỐI VỚI AI CŨ CỦA BẠN ---
# Thêm đường dẫn cha để import được module ở thư mục khác
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.ai_caro import CaroAI

# CẤU HÌNH MÀU SẮC (Dark Mode)
SIZE = 15
COLOR_BG = "#212121"       # Màu nền app
COLOR_BOARD = "#303030"    # Màu nền bàn cờ
COLOR_CELL = "#424242"     # Màu ô cờ trống
COLOR_X = "#FF5252"        # Màu quân X (Đỏ)
COLOR_O = "#448AFF"        # Màu quân O (Xanh)

class FletCaroApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Game Caro AI (Flet Version)"
        self.page.bgcolor = COLOR_BG
        self.page.window_width = 1000
        self.page.window_height = 800
        self.page.window_resizable = False
        self.page.padding = 20
        self.page.theme_mode = ft.ThemeMode.DARK # Chế độ tối

        # Logic game
        self.board_data = [[0] * SIZE for _ in range(SIZE)] # 0: Trống, 1: X, -1: O
        self.current_player = 1 
        self.game_over = False
        self.ai = CaroAI() # Kết nối với AI cũ của bạn

        # Thành phần giao diện
        self.status_txt = ft.Text(value="Lượt của bạn (X)", size=20, weight="bold", color=COLOR_X)
        self.board_ui = self.create_board_ui()
        
        # Bố cục chính (Layout)
        self.page.add(
            ft.Row(
                controls=[
                    # Bên trái: Bàn cờ
                    ft.Container(
                        content=self.board_ui, 
                        padding=10, 
                        border_radius=10, 
                        bgcolor=COLOR_BOARD,
                        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK)
                    ),
                    # Bên phải: Bảng điều khiển
                    self.create_control_panel()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    def create_board_ui(self):
        # Tạo bàn cờ bằng cách xếp các Container nhỏ
        rows_ui = []
        for r in range(SIZE):
            row_cells = []
            for c in range(SIZE):
                cell = ft.Container(
                    width=35, height=35,
                    bgcolor=COLOR_CELL,
                    border_radius=4,
                    margin=1,
                    data={"r": r, "c": c}, # Lưu tọa độ ẩn vào ô
                    on_click=self.on_cell_click,
                    on_hover=self.on_cell_hover,
                    alignment=ft.alignment.center
                )
                row_cells.append(cell)
            rows_ui.append(ft.Row(controls=row_cells, spacing=0))
        return ft.Column(controls=rows_ui, spacing=0)

    def create_control_panel(self):
        return ft.Column(
            controls=[
                ft.Text("CARO AI", size=40, weight="bold", color="white"),
                ft.Divider(color="white24"),
                self.status_txt,
                ft.Container(height=20),
                
                # Nút Chơi lại
                ft.ElevatedButton(
                    "Ván mới", 
                    icon=ft.icons.REFRESH, 
                    style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700, color="white"),
                    height=50, width=200,
                    on_click=self.reset_game
                ),
                
                # Nút Thoát
                ft.ElevatedButton(
                    "Thoát Game", 
                    icon=ft.icons.EXIT_TO_APP, 
                    style=ft.ButtonStyle(bgcolor=ft.colors.RED_700, color="white"),
                    height=50, width=200,
                    on_click=lambda e: self.page.window_close()
                ),
                
                ft.Container(height=50),
                ft.Text("Hướng dẫn:", size=16, weight="bold"),
                ft.Text("- Bạn là quân Đỏ (X)", size=14, color="grey"),
                ft.Text("- Máy là quân Xanh (O)", size=14, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

    def on_cell_hover(self, e):
        # Hiệu ứng đổi màu khi rê chuột
        if e.data == "true": # Mouse vào
            if e.control.bgcolor == COLOR_CELL:
                e.control.bgcolor = "#616161" # Sáng hơn xíu
                e.control.update()
        else: # Mouse ra
            if e.control.bgcolor == "#616161":
                e.control.bgcolor = COLOR_CELL
                e.control.update()

    def on_cell_click(self, e):
        # Hàm xử lý khi người chơi bấm vào ô
        if self.game_over or self.current_player != 1: return

        r, c = e.control.data["r"], e.control.data["c"]
        if self.board_data[r][c] != 0: return # Ô đã có quân

        # 1. Người chơi đánh
        self.execute_move(r, c, 1, e.control)
        
        # Check thắng
        if self.check_win(r, c, 1):
            self.end_game("BẠN THẮNG RỒI!", COLOR_X)
            return

        # 2. Chuyển lượt sang AI
        self.current_player = -1
        self.status_txt.value = "Máy đang suy nghĩ..."
        self.status_txt.color = COLOR_O
        self.page.update()

        # Gọi AI (chạy sau 100ms để giao diện kịp cập nhật)
        self.page.run_task(self.ai_turn)

    async def ai_turn(self):
        # AI tính toán nước đi
        move = self.ai.get_move(self.board_data)
        
        if move:
            r, c = move
            # Tìm ô trên giao diện tương ứng với tọa độ r, c
            cell_control = self.board_ui.controls[r].controls[c]
            self.execute_move(r, c, -1, cell_control)

            if self.check_win(r, c, -1):
                self.end_game("MÁY ĐÃ THẮNG!", COLOR_O)
                return

        self.current_player = 1
        self.status_txt.value = "Đến lượt bạn (X)"
        self.status_txt.color = COLOR_X
        self.page.update()

    def execute_move(self, r, c, player, control_ui):
        # Cập nhật dữ liệu logic
        self.board_data[r][c] = player
        
        # Cập nhật giao diện (Vẽ X hoặc O)
        if player == 1:
            control_ui.content = ft.Text("X", size=20, weight="bold", color="white")
            control_ui.bgcolor = COLOR_X
        else:
            control_ui.content = ft.Text("O", size=20, weight="bold", color="white")
            control_ui.bgcolor = COLOR_O
        
        control_ui.update()

    def check_win(self, r, c, player):
        # Logic kiểm tra thắng thua cơ bản
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        board = self.board_data
        for dr, dc in directions:
            count = 1
            for k in range(1, 5):
                nr, nc = r + dr*k, c + dc*k
                if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == player: count += 1
                else: break
            for k in range(1, 5):
                nr, nc = r - dr*k, c - dc*k
                if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == player: count += 1
                else: break
            if count >= 5: return True
        return False

    def end_game(self, message, color):
        self.game_over = True
        self.status_txt.value = message
        self.status_txt.color = color
        
        # Hiện thông báo đẹp
        dlg = ft.AlertDialog(
            title=ft.Text("Kết thúc"),
            content=ft.Text(message, size=20, color=color),
            actions=[
                ft.TextButton("Chơi lại", on_click=self.reset_game_dialog)
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def reset_game_dialog(self, e):
        self.page.dialog.open = False
        self.reset_game(e)

    def reset_game(self, e):
        self.board_data = [[0] * SIZE for _ in range(SIZE)]
        self.current_player = 1
        self.game_over = False
        self.status_txt.value = "Lượt của bạn (X)"
        self.status_txt.color = COLOR_X
        
        # Xóa bàn cờ (reset về ô trống)
        for row in self.board_ui.controls:
            for cell in row.controls:
                cell.content = None
                cell.bgcolor = COLOR_CELL
        self.page.update()

# Hàm chạy chính
def main(page: ft.Page):
    app = FletCaroApp(page)

if __name__ == "__main__":
    ft.app(target=main)