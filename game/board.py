class CaroBoard:
    """Class quan ly ban co Caro 15x15."""
    
    def __init__(self, size=15):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
    
    def reset_board(self):
        """Dua ban co ve trang thai ban dau."""
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]