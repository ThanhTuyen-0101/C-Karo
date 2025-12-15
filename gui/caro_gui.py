import tkinter as tk
from threading import Thread
import time
import random

# --- XỬ LÝ THƯ VIỆN ẢNH ---
try:
    from PIL import Image, ImageTk, ImageDraw, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️ LƯU Ý: Chưa cài Pillow. Hãy chạy 'pip install Pillow' để thấy ảnh tròn đẹp.")

# =================================================================================
# PHẦN 1: LOGIC & AI
# =================================================================================
class InternalBoard:
    def __init__(self, size=15):
        self.size = size
        self.board = [[0] * size for _ in range(size)]

    def place(self, row, col, player):
        if 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == 0:
            self.board[row][col] = player
            return self.check_win(row, col, player)
        return False

    def check_win(self, row, col, player):
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            for k in range(1, 5):
                r, c = row + dr*k, col + dc*k
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player: count += 1
                else: break
            for k in range(1, 5):
                r, c = row - dr*k, col - dc*k
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player: count += 1
                else: break
            if count >= 5: return True
        return False

class InternalAI:
    def get_move(self, board):
        time.sleep(0.5)
        size = len(board)
        empties = [(r, c) for r in range(size) for c in range(size) if board[r][c] == 0]
        return random.choice(empties) if empties else None

# =================================================================================
# PHẦN 2: GIAO DIỆN CARO GUI
# =================================================================================
class CaroGUI:
    def __init__(self, board_size=15, board=None, ai=None):
        # --- 1. CẤU HÌNH MÀU SẮC ---
        self.COLOR_APP_BG   = "#343434"
        self.COLOR_FRAME_BG = "#515151"
        self.COLOR_BOARD    = "#908e79"
        
        self.COLOR_TXT      = "#fcfcfc" # Màu chữ chính
        self.COLOR_X        = "#343434" 
        self.COLOR_O        = "white"   
        self.COLOR_LINE     = "#5e5c4f"  
        self.COLOR_ACCENT   = "#941e0e" 
        self.COLOR_HIGHLIGHT = "#fcfcfc" # Màu viền khi active

        # --- 2. CẤU HÌNH KÍCH THƯỚC ---
        self.outer_cols = 14    
        self.outer_rows = 12    
        self.outer_cell = 60    
        self.inner_cell = 20    
        self.size = 15          
        self.inner_px = self.size * self.inner_cell 

        self.FONT_MAIN = ("Segoe UI", 9, "bold") 
        self.FONT_BTN  = ("Segoe UI", 8, "bold") 
        self.FONT_TIMER = ("Consolas", 16, "bold")
        self.FONT_COUNTDOWN = ("Segoe UI", 40, "bold") # Font số đếm ngược

        # --- TRẠNG THÁI ---
        self.current_player = 1
        self.thinking = False
        self.game_started = False
        self.in_countdown = False # Cờ trạng thái đếm ngược
        self.history = []
        
        # --- TIMER ---
        self.time_limit = 5 * 60 
        self.current_time_left = self.time_limit
        self.timer_job = None
        
        self.images_cache = [] 
        self.current_mode = "PvM" 
        self.current_level = 2

        self.board_logic = board if board else InternalBoard(self.size)
        self.ai = ai if ai else InternalAI()

        # --- CỬA SỔ ---
        self.root = tk.Tk()
        self.root.title("Cờ Caro")
        
        win_w = self.outer_cols * self.outer_cell 
        win_h = self.outer_rows * self.outer_cell 
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.resizable(False, False)
        self.root.configure(bg=self.COLOR_APP_BG)

        # --- GIAO DIỆN ---
        self.create_background_layers() 
        self.create_board()             
        self.create_right_panel()       
        self.create_player_status_panel()

    # --------------------------------------------------------
    # HÀM HỖ TRỢ
    # --------------------------------------------------------
    def get_circular_avatar(self, image_path, size):
        if not HAS_PIL: return None
        try:
            img = Image.open(image_path).convert("RGBA")
            img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            img.putalpha(mask)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    # 1. TẠO LỚP NỀN & KHUNG
    def create_background_layers(self):
        self.bg_canvas = tk.Canvas(self.root, width=self.outer_cols*self.outer_cell, 
                                   height=self.outer_rows*self.outer_cell, 
                                   bg=self.COLOR_APP_BG, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)

        self.draw_rounded_rect(self.bg_canvas, 
                               1 * self.outer_cell, 1 * self.outer_cell, 
                               13 * self.outer_cell, 11 * self.outer_cell, 
                               radius=30, fill=self.COLOR_FRAME_BG)
        
        self.draw_rounded_rect(self.bg_canvas, 
                               8 * self.outer_cell + 10, 
                               2 * self.outer_cell + 10, 
                               12 * self.outer_cell - 10, 
                               6 * self.outer_cell - 10, 
                               radius=20, fill="", outline="#dcded0", width=2)

    # 2. TẠO BÀN CỜ
    def create_board(self):
        start_x = 2 * self.outer_cell 
        start_y = 2 * self.outer_cell 
        
        self.center_frame = tk.Frame(self.root, width=self.inner_px, height=self.inner_px, bg=self.COLOR_BOARD)
        self.center_frame.place(x=start_x, y=start_y)
        
        self.canvas = tk.Canvas(self.center_frame, width=self.inner_px, height=self.inner_px, 
                                bg=self.COLOR_BOARD, highlightthickness=0)
        self.canvas.pack()
        self.draw_grid_lines() 
        self.canvas.bind("<Button-1>", self.on_click)

    # 3. TRẠNG THÁI NGƯỜI CHƠI
    def create_player_status_panel(self):
        base_y = 9 * self.outer_cell
        center_y = base_y + (self.outer_cell // 2)

        # Avatar 1
        pos_x_p1 = 3.5 * self.outer_cell 
        self.cv_p1 = tk.Canvas(self.root, width=50, height=50, bg=self.COLOR_FRAME_BG, highlightthickness=0)
        self.cv_p1.place(x=pos_x_p1 - 25, y=center_y - 25)
        
        img_p1 = self.get_circular_avatar(r"c:\anh\nguoichoi.png", 50)
        if img_p1:
            self.images_cache.append(img_p1)
            self.cv_p1.create_image(25, 25, image=img_p1)
        else:
            self.cv_p1.create_oval(2,2,48,48, fill="gray")
            self.cv_p1.create_text(25,25, text="USER", fill="white")

        # Đồng hồ
        pos_x_timer = 4.5 * self.outer_cell
        self.lbl_timer = tk.Label(self.root, text="05:00", font=self.FONT_TIMER, 
                                  bg=self.COLOR_FRAME_BG, fg="#fcfcfc") # [MÀU MỚI]
        self.lbl_timer.place(x=pos_x_timer, y=center_y, anchor="center")
        
        lbl_note = tk.Label(self.root, text="Time Limit", font=("Segoe UI", 7), 
                            bg=self.COLOR_FRAME_BG, fg="#aaa")
        lbl_note.place(x=pos_x_timer, y=center_y + 20, anchor="center")

        # Avatar 2
        pos_x_bot = 5.5 * self.outer_cell
        self.cv_bot = tk.Canvas(self.root, width=50, height=50, bg=self.COLOR_FRAME_BG, highlightthickness=0)
        self.cv_bot.place(x=pos_x_bot - 25, y=center_y - 25)

        img_bot = self.get_circular_avatar(r"c:\anh\may.png", 50)
        if img_bot:
            self.images_cache.append(img_bot)
            self.cv_bot.create_image(25, 25, image=img_bot)
        else:
            self.cv_bot.create_oval(2,2,48,48, fill="gray")
            self.cv_bot.create_text(25,25, text="BOT", fill="white")

    # 4. PANEL PHẢI
    def create_right_panel(self):
        center_x = 10 * self.outer_cell
        center_y = 3 * self.outer_cell
        
        outer_radius = 90  
        gap = 20          
        inner_radius = outer_radius - gap 
        border_color = "#dcded0"
        cv_size = (outer_radius * 2) + 4
        
        logo_cv = tk.Canvas(self.root, width=cv_size, height=cv_size, 
                            bg=self.COLOR_FRAME_BG, highlightthickness=0)
        logo_cv.place(x=center_x - cv_size/2, y=center_y - cv_size/2)
        cc = cv_size / 2 

        logo_cv.create_oval(cc - outer_radius, cc - outer_radius, cc + outer_radius, cc + outer_radius,
                            outline=border_color, width=2, fill="")
        logo_cv.create_oval(cc - inner_radius, cc - inner_radius, cc + inner_radius, cc + inner_radius,
                            outline=border_color, width=2, fill="")

        img_size = inner_radius * 2
        photo = self.get_circular_avatar(r"c:\anh\logo.png", img_size)
        if photo:
            self.images_cache.append(photo)
            logo_cv.create_image(cc, cc, image=photo)
        else:
            logo_cv.create_oval(cc - inner_radius + 5, cc - inner_radius + 5,
                                cc + inner_radius - 5, cc + inner_radius - 5, fill="#333")
            logo_cv.create_text(cc, cc, text="LOGO", fill="white", font=("Arial", 10, "bold"))

        row_btn = 7 * self.outer_cell
        # [STYLE NÚT] Không viền
        self.draw_circle_btn("New\nGame", 8.5 * self.outer_cell, row_btn, self.reset_game)
        self.draw_circle_btn("Start", 10.5 * self.outer_cell, row_btn, self.start_countdown_sequence)

        row_mode = 8.5 * self.outer_cell
        self.btn_pvm = self.draw_mode_btn("PvM", "PvM", 8.5 * self.outer_cell, row_mode)
        self.btn_mvm = self.draw_mode_btn("MvM", "MvM", 10.5 * self.outer_cell, row_mode)
        self.update_mode_ui()

        row_slider = 9.8 * self.outer_cell
        slider_frame = tk.Frame(self.root, bg=self.COLOR_FRAME_BG)
        slider_frame.place(x=8.5 * self.outer_cell, y=row_slider, width=160, height=60)
        
        self.scale_level = tk.Scale(slider_frame, from_=1, to=3, orient=tk.HORIZONTAL, 
                                    showvalue=0, width=10, length=140,
                                    bg=self.COLOR_FRAME_BG, fg="white",
                                    troughcolor="#333", highlightthickness=0, 
                                    command=self.update_level_label)
        self.scale_level.set(2)
        self.scale_level.pack()
        self.lbl_level = tk.Label(slider_frame, text="độ khó: vừa", font=("Segoe UI", 8), bg=self.COLOR_FRAME_BG, fg="#ccc")
        self.lbl_level.pack()

    # --- HÀM VẼ UI KHÁC ---
    def draw_circle_btn(self, text, x, y, command):
        size = 50 
        cv = tk.Canvas(self.root, width=size, height=size, bg=self.COLOR_FRAME_BG, highlightthickness=0)
        cv.place(x=x, y=y)
        
        # [THAY ĐỔI] outline="" (không viền)
        oval = cv.create_oval(2, 2, size-2, size-2, fill=self.COLOR_APP_BG, outline="", width=0)
        txt = cv.create_text(size//2, size//2, text=text, font=self.FONT_BTN, fill="white", justify="center")
        
        cv.bind("<Button-1>", lambda e: command())
        cv.tag_bind(oval, "<Button-1>", lambda e: command())
        cv.tag_bind(txt, "<Button-1>", lambda e: command())

    def draw_mode_btn(self, text, mode, x, y):
        size = 50
        cv = tk.Canvas(self.root, width=size, height=size, bg=self.COLOR_FRAME_BG, highlightthickness=0)
        cv.place(x=x, y=y)
        
        # [THAY ĐỔI] outline="" ban đầu
        oval = cv.create_oval(2, 2, size-2, size-2, fill=self.COLOR_APP_BG, outline="", width=0)
        txt = cv.create_text(size//2, size//2, text=text, font=self.FONT_BTN, fill="white", justify="center")
        
        cv.bind("<Button-1>", lambda e: self.set_mode(mode))
        cv.tag_bind(oval, "<Button-1>", lambda e: self.set_mode(mode))
        cv.tag_bind(txt, "<Button-1>", lambda e: self.set_mode(mode))
        return {"cv": cv, "oval": oval, "mode": mode}

    def update_level_label(self, val):
        val = int(val)
        self.current_level = val
        texts = {1: "dễ", 2: "vừa", 3: "khó"}
        self.lbl_level.config(text=f"độ khó: {texts[val]}")

    def set_mode(self, mode):
        if self.game_started: return # Không đổi mode khi đang chơi
        self.current_mode = mode
        self.update_mode_ui()

    def update_mode_ui(self):
        # [LOGIC MỚI] Nếu chọn -> Viền #fcfcfc, width=2. Không chọn -> Không viền.
        
        # Xử lý nút PvM
        if self.current_mode == "PvM":
            self.btn_pvm["cv"].itemconfig(self.btn_pvm["oval"], outline=self.COLOR_HIGHLIGHT, width=2)
        else:
            self.btn_pvm["cv"].itemconfig(self.btn_pvm["oval"], outline="", width=0)

        # Xử lý nút MvM
        if self.current_mode == "MvM":
            self.btn_mvm["cv"].itemconfig(self.btn_mvm["oval"], outline=self.COLOR_HIGHLIGHT, width=2)
        else:
            self.btn_mvm["cv"].itemconfig(self.btn_mvm["oval"], outline="", width=0)

    def draw_grid_lines(self):
        self.canvas.delete("grid_line")
        for i in range(self.size + 1):
            pos = i * self.inner_cell
            self.canvas.create_line(pos, 0, pos, self.inner_px, fill=self.COLOR_LINE, tag="grid_line")
            self.canvas.create_line(0, pos, self.inner_px, pos, fill=self.COLOR_LINE, tag="grid_line")

    # --- LOGIC ĐẾM NGƯỢC (3, 2, 1, START) ---
    def start_countdown_sequence(self):
        if self.game_started or self.in_countdown: return
        self.reset_game()
        self.in_countdown = True
        self.run_countdown_step(3)

    def run_countdown_step(self, count):
        self.canvas.delete("countdown_text") # Xóa số cũ
        
        if count > 0:
            # Vẽ số to giữa bàn cờ
            self.canvas.create_text(self.inner_px//2, self.inner_px//2, 
                                    text=str(count), font=self.FONT_COUNTDOWN, 
                                    fill=self.COLOR_HIGHLIGHT, tag="countdown_text")
            self.root.after(1000, lambda: self.run_countdown_step(count - 1))
        else:
            # Vẽ chữ Bắt đầu
            self.canvas.create_text(self.inner_px//2, self.inner_px//2, 
                                    text="Bắt đầu", font=("Segoe UI", 30, "bold"), 
                                    fill=self.COLOR_HIGHLIGHT, tag="countdown_text")
            self.root.after(1000, self.real_game_start)

    def real_game_start(self):
        self.canvas.delete("countdown_text")
        self.in_countdown = False
        self.game_started = True
        self.current_time_left = self.time_limit
        self.start_timer()
        if self.current_mode == "MvM": self.run_auto_play()

    # --- LOGIC ĐỒNG HỒ ---
    def start_timer(self):
        if self.timer_job: self.root.after_cancel(self.timer_job)
        self.countdown_timer()

    def stop_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def countdown_timer(self):
        if not self.game_started: return
        
        mins, secs = divmod(self.current_time_left, 60)
        self.lbl_timer.config(text=f"{mins:02}:{secs:02}")

        if self.current_time_left > 0:
            self.current_time_left -= 1
            self.timer_job = self.root.after(1000, self.countdown_timer)
        else:
            self.lbl_timer.config(text="00:00", fg="red")
            self.game_started = False
            self.stop_timer()
            print("Hết giờ!")

    # --- LOGIC GAME & TƯƠNG TÁC ---
    def run_auto_play(self):
        if not self.game_started: return
        self.thinking = True
        Thread(target=self.run_ai_thread, daemon=True).start()

    def on_click(self, event):
        # Chặn click khi đang đếm ngược hoặc AI đang nghĩ
        if self.in_countdown or not self.game_started or self.thinking: return
        if self.current_mode == "MvM": return 
        
        c = event.x // self.inner_cell
        r = event.y // self.inner_cell
        if not (0 <= r < self.size and 0 <= c < self.size): return
        if self.board_logic.board[r][c] != 0: return

        self.execute_move(r, c, self.current_player)
        if self.board_logic.check_win(r, c, self.current_player):
            print("Win!")
            self.game_started = False
            self.stop_timer()
            return

        self.current_player *= -1
        if self.current_mode == "PvM" and self.current_player == -1:
             Thread(target=self.run_ai_thread, daemon=True).start()

    def execute_move(self, r, c, player):
        self.board_logic.board[r][c] = player
        self.draw_piece(r, c, player)
        self.history.append((r, c))

    def draw_piece(self, r, c, player):
        x = c * self.inner_cell; y = r * self.inner_cell; pad = 3
        if player == 1:
            self.canvas.create_line(x+pad, y+pad, x+20-pad, y+20-pad, width=2, fill=self.COLOR_X, tag="piece")
            self.canvas.create_line(x+20-pad, y+pad, x+pad, y+20-pad, width=2, fill=self.COLOR_X, tag="piece")
        else:
            self.canvas.create_oval(x+pad, y+pad, x+20-pad, y+20-pad, width=2, outline=self.COLOR_O, tag="piece")

    def reset_game(self):
        self.stop_timer()
        self.lbl_timer.config(text="05:00", fg=self.COLOR_TXT)
        self.canvas.delete("all")
        self.draw_grid_lines()
        
        if isinstance(self.board_logic, InternalBoard): self.board_logic = InternalBoard(self.size)
        else: self.board_logic.board = [[0]*self.size for _ in range(self.size)]
        
        self.history.clear()
        self.current_player = 1
        self.game_started = False
        self.thinking = False
        self.in_countdown = False

    def run_ai_thread(self):
        self.thinking = True
        move = self.ai.get_move(self.board_logic.board)
        self.root.after(0, lambda: self.after_ai_move(move))

    def after_ai_move(self, move):
        if not self.game_started: return
        if move:
            r, c = move
            if self.board_logic.board[r][c] == 0:
                self.execute_move(r, c, self.current_player)
                if self.board_logic.check_win(r, c, self.current_player):
                    print("Máy thắng")
                    self.game_started = False
                    self.thinking = False
                    self.stop_timer()
                    return
        self.thinking = False
        self.current_player *= -1
        if self.current_mode == "MvM" and self.game_started: self.root.after(500, self.run_auto_play)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CaroGUI()
    app.run()