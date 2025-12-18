import pytest
# Sửa dòng này để khớp với tên file LogicAi.py của bạn
from ai.LogicAi import find_best_move, X, O, EMPTY, SIZE 

@pytest.fixture
def empty_board():
    """Khởi tạo bàn cờ trống 15x15."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

# --- TEST LOGIC TẤN CÔNG (ATTACK) ---

def test_ai_wins_immediately(empty_board):
    """AI phải nhận ra nước đi để tạo thành đúng 5 quân và thắng ngay."""
    board = empty_board
    # Giả lập AI (O) đã có 4 quân hàng ngang từ (7,7) đến (7,10)
    for c in range(7, 11):
        board[7][c] = O
    
    # Nước đi thắng ngay là ô (7, 11) hoặc (7, 6)
    move = find_best_move(board, O)
    assert move in [(7, 11), (7, 6)]

def test_ai_completes_diagonal_win(empty_board):
    """AI phải nhận ra nước đi thắng ở hàng chéo."""
    board = empty_board
    # Giả lập AI (O) có 4 quân chéo xuống phải
    for i in range(4):
        board[5+i][5+i] = O
        
    move = find_best_move(board, O)
    assert move in [(4, 4), (9, 9)]

# --- TEST LOGIC PHÒNG THỦ (BLOCK) ---

def test_ai_blocks_opponent_four(empty_board):
    """AI phải ưu tiên chặn nước đi tạo chuỗi 4 của đối thủ (X)."""
    board = empty_board
    # Người chơi (X) đã có 3 quân tại (0,0), (0,1), (0,2)
    board[0][0] = X
    board[0][1] = X
    board[0][2] = X
    
    # AI buộc phải chặn tại (0, 3) để X không tạo được chuỗi 4 liên tiếp
    move = find_best_move(board, O)
    assert move == (0, 3)

def test_ai_prioritizes_winning_over_blocking(empty_board):
    """Nếu AI có thể thắng ngay, nó phải thắng thay vì đi chặn đối thủ."""
    board = empty_board
    # Người chơi (X) sắp thắng (đã có 4 quân hàng 0)
    for c in range(4): board[0][c] = X
    
    # AI (O) cũng sắp thắng (đã có 4 quân hàng 5)
    for c in range(4): board[5][c] = O
    
    move = find_best_move(board, O)
    # Phải chọn thắng (hàng 5) thay vì chặn (hàng 0)
    assert move in [(5, 4)]
    assert move != (0, 4)