# ================== HẰNG SỐ VÀ HƯỚNG ĐI ==================

SIZE  = 15      # Kích thước bàn cờ 15x15
EMPTY = 0       # Ô trống
X     = 1       # Quân X
O     = 2       # Quân O

# 4 hướng: ngang, dọc, chéo xuống phải, chéo xuống trái
DIRECTIONS = [
    (0, 1),
    (1, 0),
    (1, 1),
    (1, -1),
]


# ================== HÀM TIỆN ÍCH CƠ BẢN ==================

def in_board(r, c):
    """Kiểm tra (r, c) có nằm trong bàn cờ hay không."""
    return 0 <= r < SIZE and 0 <= c < SIZE


def get_opponent(player):
    """Trả về quân đối thủ của player."""
    return X if player == O else O


# ================== HÀM SINH NƯỚC ĐI HỢP LỆ (CÓ GIỚI HẠN VÙNG) ==================

def generate_legal_moves(board, radius=4):
    """
    Sinh danh sách nước đi hợp lệ (r, c).
    Tối ưu: chỉ sinh các ô trống nằm trong vùng bao quanh tất cả quân đã đánh,
    nới thêm 'radius' ô. Nếu bàn chưa có quân -> mọi ô trống đều hợp lệ.
    """
    size = len(board)
    has_stone = False
    min_r, max_r = size, -1
    min_c, max_c = size, -1

    # Tìm bounding box chứa tất cả quân
    for r in range(size):
        for c in range(size):
            if board[r][c] != EMPTY:
                has_stone = True
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)

    moves = []

    # Bàn trống -> cho phép mọi ô trống
    if not has_stone:
        for r in range(size):
            for c in range(size):
                if board[r][c] == EMPTY:
                    moves.append((r, c))
        return moves

    # Mở rộng vùng quanh quân đã đánh
    min_r = max(0, min_r - radius)
    max_r = min(size - 1, max_r + radius)
    min_c = max(0, min_c - radius)
    max_c = min(size - 1, max_c + radius)

    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            if board[r][c] == EMPTY:
                moves.append((r, c))

    # Ưu tiên ô gần trung tâm để alpha-beta cắt tỉa tốt hơn
    center = SIZE // 2
    moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))

    return moves


# ================== HÀM CHECK THẮNG (ĐÚNG 5 QUÂN) ==================

def is_exact_five(board, r, c, dr, dc):
    """
    Kiểm tra tại ô (r, c) theo hướng (dr, dc) có ĐÚNG 5 quân liên tiếp không.
    - Không tính chuỗi dài hơn 5 (overline).
    - (r, c) phải là ô ĐẦU chuỗi.
    """
    player = board[r][c]
    if player == EMPTY:
        return False

    # Kiểm tra (r, c) có phải là đầu chuỗi không
    pr, pc = r - dr, c - dc
    if in_board(pr, pc) and board[pr][pc] == player:
        return False

    # Đếm số quân liên tiếp cùng màu
    cnt = 0
    cr, cc = r, c
    while in_board(cr, cc) and board[cr][cc] == player and cnt <= 5:
        cnt += 1
        cr += dr
        cc += dc

    if cnt != 5:
        return False

    # Ô ngay sau chuỗi 5 không được cùng màu (tránh >5 quân)
    if in_board(cr, cc) and board[cr][cc] == player:
        return False

    return True


def check_winner(board):
    """Trả về X, O nếu có người thắng, None nếu chưa."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] in (X, O):
                for dr, dc in DIRECTIONS:
                    if is_exact_five(board, r, c, dr, dc):
                        return board[r][c]
    return None


# ================== HÀM ĐÁNH GIÁ (HEURISTIC) ==================

def count_sequence(board, r, c, dr, dc, player):
    """
    Đếm độ dài chuỗi liên tiếp bắt đầu tại (r, c) theo hướng (dr, dc) cho player.
    Giả sử (r, c) là ô ĐẦU chuỗi.
    """
    length = 0
    cr, cc = r, c
    while in_board(cr, cc) and board[cr][cc] == player:
        length += 1
        cr += dr
        cc += dc
    return length


def evaluate(board, player):
    """
    Đếm số chuỗi 2, 3, 4 của player và đối thủ.
    Chuỗi 2: 10 điểm
    Chuỗi 3: 50 điểm
    Chuỗi 4: 200 điểm

    Ưu tiên PHÒNG THỦ: score = score_player - 2 * score_opponent
    (đối thủ càng mạnh ở đâu thì AI càng ưu tiên chặn ở đó).
    """
    opponent = get_opponent(player)

    def score_for(p):
        total = 0
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == p:
                    for dr, dc in DIRECTIONS:
                        # Chỉ tính tại ĐẦU chuỗi để không đếm trùng
                        pr, pc = r - dr, c - dc
                        if in_board(pr, pc) and board[pr][pc] == p:
                            continue
                        length = count_sequence(board, r, c, dr, dc, p)
                        if length == 2:
                            total += 10
                        elif length == 3:
                            total += 50
                        elif length == 4:
                            total += 200
        return total

    my_score = score_for(player)
    opp_score = score_for(opponent)

    return my_score - 2 * opp_score   # hệ số 2 để phòng thủ mạnh hơn


# ================== MINIMAX + ALPHA–BETA PRUNING ==================

def minimax_ab(board, depth, alpha, beta, maximizing, player):
    """
    Minimax có cắt tỉa alpha–beta.
    Trả về (giá_trị_minimax, nước_đi_tốt_nhất).
    """
    winner = check_winner(board)
    if winner == player:
        return 10_000, None
    elif winner == get_opponent(player):
        return -10_000, None

    if depth == 0:
        return evaluate(board, player), None

    moves = generate_legal_moves(board)
    if not moves:
        return 0, None  # hòa

    if maximizing:
        best_val = -float("inf")
        best_move = None
        for r, c in moves:
            board[r][c] = player
            val, _ = minimax_ab(board, depth - 1, alpha, beta, False, player)
            board[r][c] = EMPTY

            if val > best_val:
                best_val = val
                best_move = (r, c)

            if best_val > alpha:
                alpha = best_val
            if beta <= alpha:
                break

        return best_val, best_move
    else:
        opp = get_opponent(player)
        best_val = float("inf")
        best_move = None
        for r, c in moves:
            board[r][c] = opp
            val, _ = minimax_ab(board, depth - 1, alpha, beta, True, player)
            board[r][c] = EMPTY

            if val < best_val:
                best_val = val
                best_move = (r, c)

            if best_val < beta:
                beta = best_val
            if beta <= alpha:
                break

        return best_val, best_move


def find_best_move(board, player, depth=3):
    """
    Chọn nước đi tốt nhất cho 'player' trên 'board' bằng Minimax + Alpha–Beta.
    """
    _, move = minimax_ab(board, depth, -float("inf"), float("inf"), True, player)
    if move is None:
        moves = generate_legal_moves(board)
        if moves:
            return moves[0]
    return move


# ================== VÍ DỤ CHẠY THỬ TRONG CONSOLE ==================

if __name__ == "__main__":
    board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
    best = find_best_move(board, X, depth=3)
    print("Best move for X:", best)
