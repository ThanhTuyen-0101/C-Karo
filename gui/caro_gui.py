import flet as ft
import asyncio

# === CẤU HÌNH MÀU SẮC ===
MAIN_BG_COLOR = "#f9e27d"       # Nền vàng
MENU_BG_COLOR = "#f9e27d"       # Nền menu
TEXT_COLOR = "#000000"          # Màu chữ Đen

# Cấu hình bàn cờ
BOARD_BG_COLOR = "#ffffff"      # Nền trắng
BOARD_LINE_COLOR = "#000000"    # Kẻ đen

X_COLOR = "#d32f2f"
O_COLOR = "#1976d2"

# === CẤU HÌNH KÍCH THƯỚC ===
MENU_WIDTH = 400
BOARD_SIZE = 500
TOP_OFFSET = 175

TOTAL_WIDTH = MENU_WIDTH + BOARD_SIZE
TOTAL_HEIGHT = BOARD_SIZE + TOP_OFFSET

BLOCK_COUNT = 5
SUB_CELL_COUNT = 3


class CaroGUI:
    def __init__(self, page: ft.Page, board_logic, ai_engine):
        self.page = page
        self.board_logic = board_logic
        self.ai = ai_engine

        self.page.title = "Game Caro Big Win Notification"
        self.page.bgcolor = MAIN_BG_COLOR
        self.page.padding = 0
        self.page.margin = 0
        self.page.spacing = 0

        # Font chữ Fredoka One (Tròn, Mập, Đậm)
        self.page.fonts = {
            "FredokaOne": "https://raw.githubusercontent.com/google/fonts/master/ofl/fredokaone/FredokaOne-Regular.ttf"
        }
        self.page.theme = ft.Theme(font_family="FredokaOne")

        # === CẤU HÌNH CỬA SỔ ===
        self.page.window_width = TOTAL_WIDTH + 16
        self.page.window_height = TOTAL_HEIGHT + 39
        self.page.window_resizable = False
        self.page.window_maximizable = False
        
        # --- (MỚI) KHỞI TẠO ÂM THANH ---
        # Lưu ý: File phải nằm trong thư mục 'amthanh' cùng cấp với file chạy
        self.audio_click = ft.Audio(src="amthanh/cach.mp3", autoplay=False)
        self.audio_win = ft.Audio(src="amthanh/votay.mp3", autoplay=False)
        self.audio_lose = ft.Audio(src="amthanh/khoc.mp3", autoplay=False)
        
        # Thêm vào overlay để luôn sẵn sàng phát
        self.page.overlay.extend([self.audio_click, self.audio_win, self.audio_lose])
        
        self.page.update()

        self.is_playing = False
        self.history = []
        self.game_mode = "PvM"
        self.level = 1
        self.ui_cells = {}
        self.win_overlay_container = None # Biến lưu overlay thắng

        # --- GIAO DIỆN CHÍNH ---
        self.page.add(
            ft.Row(
                width=TOTAL_WIDTH,
                height=TOTAL_HEIGHT,
                spacing=0,
                controls=[
                    # 1. MENU
                    ft.Container(
                        width=MENU_WIDTH,
                        height=TOTAL_HEIGHT,
                        bgcolor=MENU_BG_COLOR,
                        padding=25,
                        
                        shadow=ft.BoxShadow(
                            blur_radius=15,
                            spread_radius=1,
                            color="#26000000",
                            offset=ft.Offset(4, 0)
                        ),
                        
                        alignment=ft.alignment.center,
                        content=self.create_menu_compact()
                    ),

                    # 2. BÀN CỜ + ẢNH
                    ft.Container(
                        width=BOARD_SIZE,
                        height=TOTAL_HEIGHT,
                        content=ft.Column(
                            spacing=0,
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                # Ảnh
                                ft.Container(
                                    height=TOP_OFFSET,
                                    width=BOARD_SIZE,
                                    alignment=ft.alignment.bottom_center,
                                    padding=ft.padding.only(bottom=10),
                                    content=ft.Image(
                                        src="anh/binhthuong.png",
                                        fit=ft.ImageFit.CONTAIN,
                                        error_content=ft.Text("Chưa có ảnh", color="red")
                                    )
                                ),
                                # Bàn cờ
                                self.create_board_square()
                            ]
                        )
                    )
                ]
            )
        )

    # --- MENU ĐIỀU KHIỂN ---
    def create_menu_compact(self):
        self.cb_pvm = ft.Checkbox(
            label="Người vs Máy",
            value=True,
            fill_color="black",
            check_color="white",
            label_style=ft.TextStyle(color=TEXT_COLOR, size=16),
            on_change=self.on_mode_checkbox_change
        )

        self.cb_mvm = ft.Checkbox(
            label="Máy vs Máy",
            value=False,
            fill_color="black",
            check_color="white",
            label_style=ft.TextStyle(color=TEXT_COLOR, size=16),
            on_change=self.on_mode_checkbox_change
        )

        self.slider_level = ft.Slider(
            min=1, max=3, divisions=2, value=1,
            label="{value}",
            active_color="black",
            thumb_color="black",
            on_change=self.on_level_change
        )

        level_label = self.get_level_text(self.level)
        self.level_text = ft.Text(level_label, color="black", size=20)

        return ft.Column(
            controls=[
                ft.Text("GAME CARO", size=45, text_align="center", color=TEXT_COLOR),
                ft.Divider(height=30, color="transparent"),
                
                ft.Text("Chế độ:", color=TEXT_COLOR, size=18),
                
                ft.Row(
                    width=320,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[self.cb_pvm, self.cb_mvm]
                ),

                ft.Divider(height=20, color="transparent"),
                
                ft.Row(
                    width=320,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Độ khó:", color=TEXT_COLOR, size=18),
                        self.level_text
                    ]
                ),
                
                self.slider_level,
                
                ft.Divider(height=40, color="transparent"),
                
                self.create_btn("BẮT ĐẦU", self.on_start_click),
                ft.Container(height=15),
                self.create_btn("QUAY LẠI", self.on_undo_click),
                ft.Container(height=15),
                self.create_btn("MÀN MỚI", self.reset_game_ui),
            ],
            horizontal_alignment="center",
            alignment=ft.MainAxisAlignment.CENTER
        )

    def get_level_text(self, level):
        if level == 1: return "Dễ"
        if level == 2: return "Vừa"
        return "Khó"

    def on_mode_checkbox_change(self, e):
        if e.control == self.cb_pvm and self.cb_pvm.value == True:
            self.cb_mvm.value = False
            self.game_mode = "PvM"
        elif e.control == self.cb_mvm and self.cb_mvm.value == True:
            self.cb_pvm.value = False
            self.game_mode = "MvM"
        elif self.cb_pvm.value == False and self.cb_mvm.value == False:
            e.control.value = True
        self.cb_pvm.update()
        self.cb_mvm.update()

    def create_btn(self, text, func):
        return ft.ElevatedButton(
            text=text,
            height=55,
            width=320,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
                text_style=ft.TextStyle(size=18, weight="bold"),
                
                bgcolor={
                    ft.ControlState.HOVERED: "black",
                    ft.ControlState.PRESSED: "black",
                    ft.ControlState.DEFAULT: "white"
                },
                
                color={
                    ft.ControlState.HOVERED: "white",
                    ft.ControlState.PRESSED: "white",
                    ft.ControlState.DEFAULT: "black"
                },
                
                overlay_color="#333333"
            ),
            on_click=func
        )

    # --- BÀN CỜ ---
    def create_board_square(self):
        BOARD_PADDING = 20
        
        macro_rows = []
        for r_block in range(BLOCK_COUNT):
            row_blocks = []
            for c_block in range(BLOCK_COUNT):
                micro_rows = []
                for r_sub in range(SUB_CELL_COUNT):
                    micro_cells = []
                    for c_sub in range(SUB_CELL_COUNT):
                        real_r = r_block * SUB_CELL_COUNT + r_sub
                        real_c = c_block * SUB_CELL_COUNT + c_sub

                        cell_text = ft.Text(
                            "",
                            size=20,
                            text_align=ft.TextAlign.CENTER,
                            no_wrap=True
                        )
                        self.ui_cells[(real_r, real_c)] = cell_text

                        cell = ft.Container(
                            expand=1,
                            bgcolor="#00000000",
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=5),
                            content=cell_text,
                            data={"r": real_r, "c": real_c},
                            on_click=self.on_cell_click,
                            border=ft.border.all(1.0, BOARD_LINE_COLOR),
                            border_radius=0
                        )
                        micro_cells.append(cell)
                    micro_rows.append(ft.Row(micro_cells, spacing=0, expand=1))

                block = ft.Container(
                    expand=1,
                    content=ft.Column(micro_rows, spacing=0, expand=True),
                    border=None
                )
                row_blocks.append(block)
            macro_rows.append(ft.Row(row_blocks, spacing=0, expand=1))

        return ft.Container(
            width=BOARD_SIZE - (BOARD_PADDING * 2),
            height=BOARD_SIZE - (BOARD_PADDING * 2),
            content=ft.Column(macro_rows, spacing=0, expand=True),
            bgcolor=BOARD_BG_COLOR,
            border=ft.border.all(2, BOARD_LINE_COLOR),
            border_radius=0,
            shadow=None
        )

    # --- LOGIC ---
    def on_level_change(self, e):
        self.level = int(e.control.value)
        self.level_text.value = self.get_level_text(self.level)
        self.level_text.update()

    async def on_start_click(self, e):
        if self.is_playing: return
        
        # Đếm ngược
        cnt_text = ft.Text("3", size=100, color="black", font_family="FredokaOne", weight="bold")
        overlay = ft.Container(
            content=cnt_text,
            alignment=ft.alignment.center,
            bgcolor="#ccffffff",
            expand=True,
            on_click=lambda _: None
        )
        
        self.page.overlay.append(overlay)
        self.page.update()
        
        for i in range(3, 0, -1):
            cnt_text.value = str(i)
            cnt_text.update()
            await asyncio.sleep(1)
            
        cnt_text.value = "BẮT ĐẦU!"
        cnt_text.size = 60
        cnt_text.update()
        await asyncio.sleep(0.8)
        
        self.page.overlay.remove(overlay)
        self.page.update()
        
        self.is_playing = True
        self.clear_visuals()
        if hasattr(self.board_logic, 'reset_board'): self.board_logic.reset_board()
        self.history = []
        
        if self.game_mode == "MvM":
            self.page.run_task(self.run_mvm)

    def on_cell_click(self, e):
        if not self.is_playing or self.game_mode == "MvM": return
        r, c = e.control.data["r"], e.control.data["c"]
        if self.board_logic.board[r][c] != 0: return
        
        self.move(r, c, 1)
        # Kiểm tra thắng ngay sau nước đi của bạn
        if self.check_win_gui(r, c, 1): return
        
        self.page.run_task(self.ai_move)

    async def ai_move(self):
        await asyncio.sleep(0.3)
        try: 
            m = self.ai.get_move(self.board_logic.board, level=self.level)
        except TypeError: 
            m = self.ai.get_move(self.board_logic.board)
        except Exception as e:
            print(f"AI Error: {e}")
            return
        
        if m:
            self.move(m[0], m[1], -1)
            self.page.update()
            self.check_win_gui(m[0], m[1], -1)
        else:
            print("AI returned None move")

    async def run_mvm(self):
        while self.is_playing:
            await asyncio.sleep(0.4)
            try: m1 = self.ai.get_move(self.board_logic.board, level=self.level)
            except TypeError: m1 = self.ai.get_move(self.board_logic.board)
            if m1 and self.board_logic.board[m1[0]][m1[1]] == 0:
                self.move(m1[0], m1[1], 1)
                if self.check_win_gui(m1[0], m1[1], 1): break
            await asyncio.sleep(0.4)
            try: m2 = self.ai.get_move(self.board_logic.board, level=self.level)
            except TypeError: m2 = self.ai.get_move(self.board_logic.board)
            if m2 and self.board_logic.board[m2[0]][m2[1]] == 0:
                self.move(m2[0], m2[1], -1)
                if self.check_win_gui(m2[0], m2[1], -1): break

    def move(self, r, c, p):
        self.board_logic.board[r][c] = p
        self.history.append((r, c))
        if (r, c) in self.ui_cells:
            self.ui_cells[(r, c)].value = "X" if p == 1 else "O"
            self.ui_cells[(r, c)].color = X_COLOR if p == 1 else O_COLOR
            self.ui_cells[(r, c)].update()
            
            # --- (MỚI) PHÁT ÂM THANH KHI ĐÁNH ---
            try:
                self.audio_click.play()
            except Exception as ex:
                print("Lỗi phát âm thanh:", ex)

    def check_5_in_a_row(self, r, c, player):
        board = self.board_logic.board
        rows = len(board)
        cols = len(board[0])
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                nr, nc = r + dr * i, c + dc * i
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == player: count += 1
                else: break
            for i in range(1, 5):
                nr, nc = r - dr * i, c - dc * i
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == player: count += 1
                else: break
            if count >= 5: return True
        return False

    def check_win_gui(self, r, c, p):
        if self.check_5_in_a_row(r, c, p):
            winner_msg = ""
            if self.game_mode == "PvM":
                if p == 1:
                    winner_msg = "BẠN THẮNG!"
                    self.audio_win.play() # --- (MỚI) ÂM THANH THẮNG
                else:
                    winner_msg = "MÁY THẮNG!"
                    self.audio_lose.play() # --- (MỚI) ÂM THANH THUA
            else:
                winner_msg = "MÁY X THẮNG!" if p == 1 else "MÁY O THẮNG!"
                self.audio_win.play() # --- (MỚI) ÂM THANH THẮNG CHUNG CHO MÁY

            self.is_playing = False
            
            # --- SHOW OVERLAY THÔNG BÁO THẮNG (TO NHƯ 3-2-1) ---
            self.show_win_overlay(winner_msg)
            return True
        return False

    def show_win_overlay(self, text):
        # Tạo nội dung thông báo
        content = ft.Column(
            controls=[
                ft.Text(text, size=80, color="black", font_family="FredokaOne", weight="bold", text_align="center"),
                ft.Container(height=20),
                self.create_btn("ĐÓNG", self.close_win_overlay)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.win_overlay_container = ft.Container(
            content=content,
            alignment=ft.alignment.center,
            bgcolor="#ccffffff", # Mờ trắng
            expand=True,
            on_click=lambda _: None # Chặn click
        )
        
        self.page.overlay.append(self.win_overlay_container)
        self.page.update()

    def close_win_overlay(self, e):
        if self.win_overlay_container in self.page.overlay:
            self.page.overlay.remove(self.win_overlay_container)
            self.page.update()

    def on_undo_click(self, e):
        if not self.history: return
        steps_to_undo = 0
        if self.game_mode == "PvM":
             steps_to_undo = 2 if len(self.history) >= 2 else len(self.history)
        else:
             steps_to_undo = 1
        for _ in range(steps_to_undo):
            if self.history:
                r, c = self.history.pop()
                self.board_logic.board[r][c] = 0
                if (r, c) in self.ui_cells:
                    self.ui_cells[(r, c)].value = ""
                    self.ui_cells[(r, c)].update()

    def reset_game_ui(self, e):
        self.is_playing = False
        self.history = []
        if hasattr(self.board_logic, 'reset_board'):
             self.board_logic.reset_board()
        else:
             self.board_logic.board = [[0] * 15 for _ in range(15)]
        self.clear_visuals()
        # Đóng overlay nếu còn
        if self.win_overlay_container in self.page.overlay:
            self.page.overlay.remove(self.win_overlay_container)
            self.page.update()

    def clear_visuals(self):
        for cell in self.ui_cells.values():
            cell.value = ""
            cell.update()