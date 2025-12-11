# game/board.py
class CaroBoard:
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
           
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1; r += dr; c += dc
           
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1; r -= dr; c -= dc
            if count >= 5:
                return True
        return False