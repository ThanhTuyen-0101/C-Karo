class CaroBoard:
    X_MARK = 1
    O_MARK = -1
    EMPTY_MARK = 0

    def __init__(self, size=15):
        self.size = size
        self.reset()

    def reset(self):
        """Đưa bàn cờ về trạng thái ban đầu."""
        self.board = [[self.EMPTY_MARK for _ in range(self.size)] for _ in range(self.size)]
        self.current = self.X_MARK
        self.move_count = 0

    def in_bounds(self, r, c):
        """Luật Biên: Đảm bảo tọa độ không nằm ngoài mảng."""
        return 0 <= r < self.size and 0 <= c < self.size

    def place(self, r, c):
        """Luật Đặt Quân: Kiểm tra tính hợp lệ và cập nhật bàn cờ."""
        if not self.in_bounds(r, c):
            return False, "Ngoài bàn cờ"
        if self.board[r][c] != self.EMPTY_MARK:
            return False, "Ô đã có quân"

        self.board[r][c] = self.current
        self.move_count += 1
        return True, None

    def check_win(self, r, c):
        """Luật Thắng: Kiểm tra chuỗi đúng 5 quân tại 4 hướng."""
        player_mark = self.board[r][c] 
        if player_mark == self.EMPTY_MARK: return False
        
        # Hướng: Ngang, Dọc, Chéo xuôi, Chéo ngược
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Duyệt tiến và lùi để đếm tổng số quân liên tiếp
            for direction in [1, -1]:
                i = 1
                while True:
                    nr, nc = r + dr * i * direction, c + dc * i * direction
                    if self.in_bounds(nr, nc) and self.board[nr][nc] == player_mark:
                        count += 1
                        i += 1
                    else:
                        break

            # Luật Đúng 5 Quân
            if count == 5:
                return True
        return False

    def is_draw(self):
        """Luật Hòa: Bàn cờ không còn ô trống."""
        return self.move_count == self.size * self.size

    def switch_player(self):
        """Đổi lượt: X thành O và ngược lại."""
        self.current *= -1