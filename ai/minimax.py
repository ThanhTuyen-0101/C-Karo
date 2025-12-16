# ================== HẰNG SỐ VÀ HƯỚNG ĐI ==================

SIZE  = 15      # Kích thước bàn cờ 15x15
EMPTY = 0       # Ô trống
X     = 1       # Quân X
O     = 2       # Quân O

# 4 hướng chính để kiểm tra: ngang, dọc, chéo xuống phải, chéo xuống trái
DIRECTIONS = [
    (0, 1),     # ngang
    (1, 0),     # dọc
    (1, 1),     # chéo xuống phải
    (1, -1),    # chéo xuống trái
]


# ================== HÀM TIỆN ÍCH CƠ BẢN ==================

def in_board(r, c):
    """
    Kiểm tra (r, c) có nằm trong bàn cờ hay không.
    Trả về True nếu nằm trong, False nếu ngoài.
    """
    return 0 <= r < SIZE and 0 <= c < SIZE


def get_opponent(player):
    """
    Trả về quân đối thủ của player.
    Nếu player là X thì trả về O, ngược lại.
    """
    return X if player == O else O


# ================== HÀM SINH NƯỚC ĐI HỢP LỆ (ƯU TIÊN GẦN QUÂN NGƯỜI) ==================

def generate_legal_moves(board, radius=4):
    """
    Sinh danh sách các nước đi hợp lệ (r, c).

    Tối ưu:
    - Chỉ sinh các ô trống nằm trong vùng bao quanh tất cả quân đã đánh,
      nới thêm 'radius' ô.
    - Bàn trống -> mọi ô trống đều hợp lệ.
    - Sắp xếp moves: ưu tiên nước đi gần QUÂN NGƯỜI chơi (X) trước,
      để AI dễ chặn hơn.
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

    # --- SẮP XẾP: ƯU TIÊN GẦN QUÂN NGƯỜI CHƠI (X) ---
    opp_cells = [(r, c) for r in range(size) for c in range(size)
                 if board[r][c] == X]  # giả sử người chơi là X

    if opp_cells:
        def dist_to_opp(m):
            r, c = m
            # khoảng cách Manhattan tới quân người gần nhất
            return min(abs(r - orr) + abs(c - occ) for orr, occ in opp_cells)
        moves.sort(key=dist_to_opp)
    else:
        # nếu chưa có quân người -> ưu tiên gần trung tâm
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
        # Nếu ô trước đó cùng màu => không phải đầu chuỗi
        return False

    # Đếm số quân liên tiếp cùng màu
    cnt = 0
    cr, cc = r, c
    while in_board(cr, cc) and board[cr][cc] == player and cnt <= 5:
        cnt += 1
        cr += dr
        cc += dc

    # Phải đúng 5 quân
    if cnt != 5:
        return False

    # Ô ngay sau chuỗi 5 không được cùng màu (tránh >5 quân)
    if in_board(cr, cc) and board[cr][cc] == player:
        return False

    return True


def check_winner(board):
    """
    Kiểm tra xem có người thắng chưa.
    Trả về:
    - X hoặc O nếu có người thắng (đúng 5 quân liên tiếp).
    - None nếu chưa ai thắng.
    """
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
    Giả sử (r, c) là ô ĐẦU chuỗi (đã kiểm tra bên ngoài).
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
    Hàm heuristic đơn giản để đánh giá trạng thái bàn cờ đối với player.

    Ý tưởng:
    - Đếm số chuỗi 2, 3, 4 của player và của đối thủ.
    - Cho điểm:
      + Chuỗi 2: 10 điểm
      + Chuỗi 3: 50 điểm
      + Chuỗi 4: 200 điểm
    - ƯU TIÊN PHÒNG THỦ:
      score = score_player - 3 * score_opponent
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
    return my_score - 3 * opp_score  # nhân 3 để ưu tiên chặn đối thủ


# ================== MINIMAX + ALPHA–BETA PRUNING ==================

def minimax_ab(board, depth, alpha, beta, maximizing, player):
    """
    Thuật toán Minimax có cắt tỉa alpha–beta.

    Tham số:
    - board      : trạng thái bàn cờ hiện tại
    - depth      : độ sâu tìm kiếm còn lại
    - alpha      : giá trị tốt nhất hiện tại của nhánh MAX
    - beta       : giá trị tốt nhất hiện tại của nhánh MIN
    - maximizing : True nếu đang đến lượt player (MAX), False nếu lượt đối thủ (MIN)
    - player     : quân mà AI điều khiển (X hoặc O)

    Trả về:
    - (giá_trị_minimax, nước_đi_tốt_nhất)
    """
    # 1. Kiểm tra thắng/thua sớm
    winner = check_winner(board)
    if winner == player:
        return 10_000, None            # player thắng
    elif winner == get_opponent(player):
        return -10_000, None           # đối thủ thắng

    # 2. Nếu đạt độ sâu giới hạn thì trả về giá trị heuristic
    if depth == 0:
        return evaluate(board, player), None

    # 3. Sinh các nước đi hợp lệ
    moves = generate_legal_moves(board)
    if not moves:
        return 0, None                  # hòa

    # 4. Nhánh MAX (AI)
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

    # 5. Nhánh MIN (đối thủ)
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
    Hàm public để AI chọn nước đi tốt nhất cho 'player' trên 'board'
    bằng Minimax + Alpha–Beta.
    """
    _, move = minimax_ab(board, depth, -float("inf"), float("inf"), True, player)
    if move is None:
        moves = generate_legal_moves(board)
        if moves:
            return moves[0]
    return move


# ================== VÍ DỤ CHẠY THỬ TRONG CONSOLE ==================

if __name__ == "__main__":
    # Khởi tạo bàn cờ trống 15x15
    board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

    # Ví dụ: cho AI chơi quân X, tìm nước đi tốt nhất ở trạng thái ban đầu
    best = find_best_move(board, X, depth=3)
    print("Best move for X:", best)
