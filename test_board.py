import pytest
from game.board import CaroBoard

@pytest.fixture
def board():
    """Khởi tạo bàn cờ mới 15x15 cho mỗi bài test."""
    return CaroBoard(size=15)

# --- TEST LUẬT ĐẶT QUÂN ---
def test_place_piece_logic(board):
    """Kiểm tra đặt quân thành công và tăng biến đếm move_count."""
    ok, msg = board.place(7, 7)
    assert ok is True
    assert board.board[7][7] == board.X_MARK
    assert board.move_count == 1

def test_place_on_occupied_cell(board):
    """Kiểm tra không cho phép đặt đè lên quân đã có."""
    board.place(5, 5)
    ok, msg = board.place(5, 5)
    assert ok is False
    assert msg == "Ô đã có quân"

# --- TEST LUẬT THẮNG (ĐÚNG 5 QUÂN) ---
def test_win_with_exactly_five(board):
    """Kiểm tra thắng khi có đúng 5 quân hàng ngang."""
    # Giả lập đặt 5 quân X hàng ngang từ (0,0) đến (0,4)
    for c in range(5):
        board.board[0][c] = board.X_MARK
    
    # Kiểm tra tại vị trí bất kỳ trong chuỗi 5 quân
    assert board.check_win(0, 2) is True

def test_six_pieces_no_win(board):
    """KIỂM TRA LUẬT 6 QUÂN: count == 5 mới thắng, 6 quân phải trả về False."""
    # Giả lập chuỗi 6 quân X hàng ngang
    for c in range(6):
        board.board[2][c] = board.X_MARK
    
    # Với logic 'if count == 5:', chuỗi 6 quân sẽ không thắng
    assert board.check_win(2, 3) is False

def test_diagonal_win(board):
    """Kiểm tra thắng hàng chéo chính."""
    for i in range(5):
        board.board[i][i] = board.X_MARK
    assert board.check_win(2, 2) is True

# --- TEST LUẬT HÒA ---
def test_draw_logic():
    """Kiểm tra trạng thái hòa khi move_count lấp đầy bàn cờ."""
    size = 3
    small_board = CaroBoard(size=size)
    # Lấp đầy bàn cờ 3x3 (9 ô)
    for r in range(size):
        for c in range(size):
            small_board.place(r, c)
            
    assert small_board.move_count == 9
    assert small_board.is_draw() is True