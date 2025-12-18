# ================== HÀNG SỐ VÀ HUỚNG ĐI ==================

SIZE = 15        # Kích thước bàn cờ 15x15
EMPTY = 0        # Ô trống
X = 1            # Quân X (người chơi)
O = -1           # Quân O (AI)
# 4 hướng chính: ngang, dọc, chéo xuống phải, chéo xuống trái
DIRECTIONS = [
    (0, 1),    # Ngang (phải)
    (1, 0),    # Dọc (xuống)
    (1, 1),    # Chéo xuống phải
    (1, -1),   # Chéo xuống trái
]

# ================== HÀM TIỆN ÍCH CƠ BẢN ==================

def in_board(r, c):
    """Kiểm tra tọa độ (r, c) có nằm trong bàn cờ không."""
    return 0 <= r < SIZE and 0 <= c < SIZE

def get_opponent(player):
    """Trả về quân đối thủ của player."""
    return X if player == O else O

# ================== SINH NƯỚC ĐI HỢP LỆ (ƯU TIÊN GẦN NGƯỜI) ==================

def generate_legal_moves(board, radius=4):
    """
    Sinh danh sách nước đi hợp lệ (r, c).
    
    - Chỉ sinh ô trống trong vùng bao quanh quân đã đánh + 'radius' ô.
    - Bàn trống -> mọi ô trống đều hợp lệ.
    - Sắp xếp: ưu tiên nước gần QUÂN NGƯỜI (X) trước để AI dễ chọn.
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

    # ƯU TIÊN GẦN QUÂN NGƯỜI (X)
    opp_cells = [(r, c) for r in range(size) for c in range(size)
                 if board[r][c] == X]

    if opp_cells:
        def dist_to_opp(m):
            r, c = m
            return min(abs(r - orr) + abs(c - occ) for orr, occ in opp_cells)
        moves.sort(key=dist_to_opp)
    else:
        # Nếu chưa có quân người -> ưu tiên gần tâm
        center = SIZE // 2
        moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))

    return moves

# ================== KIỂM TRA THẮNG (ĐÚNG 5 QUÂN) ==================

def is_exact_five(board, r, c, dr, dc):
    """
    Kiểm tra tại ô (r, c) theo hướng (dr, dc) có ĐÚNG 5 quân liên tiếp không.
    - Không tính chuỗi dài hơn 5 (overline).
    - (r, c) phải là ô ĐẦU chuỗi.
    """
    player = board[r][c]
    if player == EMPTY:
        return False

    # Kiểm tra không có quân trước đầu chuỗi
    pr, pc = r - dr, c - dc
    if in_board(pr, pc) and board[pr][pc] == player:
        return False

    # Đếm chuỗi tiến
    cnt = 0
    cr, cc = r, c
    while in_board(cr, cc) and board[cr][cc] == player and cnt <= 5:
        cnt += 1
        cr += dr
        cc += dc

    if cnt != 5:
        return False

    # Kiểm tra không có quân sau cuối chuỗi
    if in_board(cr, cc) and board[cr][cc] == player:
        return False

    return True

def check_winner(board):
    """Trả về X hoặc O nếu có người thắng, None nếu chưa."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] in (X, O):
                for dr, dc in DIRECTIONS:
                    if is_exact_five(board, r, c, dr, dc):
                        return board[r][c]
    return None

# ================== HÀM ĐÁNH GIÁ (HEURISTIC) ==================

def count_sequence(board, r, c, dr, dc, player):
    """Đếm độ dài chuỗi liên tiếp bắt đầu tại (r,c) theo hướng (dr,dc)."""
    length = 0
    cr, cc = r, c
    while in_board(cr, cc) and board[cr][cc] == player:
        length += 1
        cr += dr
        cc += dc
    return length

def evaluate(board, player):
    """
    Đánh giá trạng thái bàn cờ cho player.
    
    - Chuỗi 2: 10 điểm
    - Chuỗi 3: 50 điểm  
    - Chuỗi 4: 200 điểm
    - score = my_score - 3 * opp_score (phòng thủ mạnh)
    """
    opponent = get_opponent(player)

    def score_for(p):
        total = 0
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == p:
                    for dr, dc in DIRECTIONS:
                        # Bỏ qua nếu không phải đầu chuỗi
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
    return my_score - 3 * opp_score

# ================== TÌM NƯỚC CHẶN BẮT BUỘC ==================

def find_block_move(board, player):
    """
    Tìm nước đi CHẶN đối thủ.
    Ưu tiên:
    1) Chặn ô đối thủ tạo chuỗi >= 4
    2) Chặn ô đối thủ tạo chuỗi = 3
    """
    opponent = get_opponent(player)
    size = len(board)

    block_four = None
    block_three = None

    for r in range(size):
        for c in range(size):
            if board[r][c] != EMPTY:
                continue

            # Thử đặt quân đối thủ
            board[r][c] = opponent
            max_len = 1

            # Kiểm tra 4 hướng
            for dr, dc in DIRECTIONS:
                length = 1
                # Hướng tiến
                cr, cc = r + dr, c + dc
                while in_board(cr, cc) and board[cr][cc] == opponent:
                    length += 1
                    cr += dr
                    cc += dc
                # Hướng lùi  
                cr, cc = r - dr, c - dc
                while in_board(cr, cc) and board[cr][cc] == opponent:
                    length += 1
                    cr -= dr
                    cc -= dc

                if length > max_len:
                    max_len = length

            board[r][c] = EMPTY  # Hoàn tác

            if max_len >= 4:
                return (r, c)  # Chặn chuỗi 4+ -> ưu tiên cao nhất
            elif max_len == 3 and block_three is None:
                block_three = (r, c)

    return block_three

# ================== TÌM NƯỚC TẤN CÔNG BẮT BUỘC ==================

def find_attack_move(board, player):
    """
    Tìm nước đi TẤN CÔNG cho player (AI).
    Chỉ ưu tiên nước ĐÁNH VÀO LÀ THẮNG NGAY (chuỗi >=5).
    """
    size = len(board)

    for r in range(size):
        for c in range(size):
            if board[r][c] != EMPTY:
                continue

            # Giả lập player đánh vào (r, c)
            board[r][c] = player
            max_len = 1

            # Kiểm tra 4 hướng
            for dr, dc in DIRECTIONS:
                length = 1
                # Hướng tiến
                cr, cc = r + dr, c + dc
                while in_board(cr, cc) and board[cr][cc] == player:
                    length += 1
                    cr += dr
                    cc += dc
                # Hướng lùi
                cr, cc = r - dr, c - dc
                while in_board(cr, cc) and board[cr][cc] == player:
                    length += 1
                    cr -= dr
                    cc -= dc

                if length > max_len:
                    max_len = length

            board[r][c] = EMPTY  # Hoàn tác

            if max_len >= 5:
                # Đánh vào là có chuỗi 5+ -> chọn ngay
                return (r, c)

    return None

# ================== MINIMAX + ALPHA-BETA PRUNING ==================

def minimax_ab(board, depth, alpha, beta, maximizing, player):
    """
    Minimax với cắt tỉa alpha-beta.
    Trả về (giá trị, nước đi tốt nhất).
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
        return 0, None

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

            alpha = max(alpha, best_val)
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

            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val, best_move

# ================== CHỌN NƯỚC ĐI CUỐI CÙNG ==================

def find_best_move(board, player, depth=3):
    """
    Thứ tự ưu tiên:
    1) TẤN CÔNG (thắng ngay)
    2) CHẶN (chuỗi 4, rồi chuỗi 3 của đối thủ)
    3) Minimax + Alpha-Beta
    """
    # 1. Kiểm tra nước thắng ngay
    attack_move = find_attack_move(board, player)
    if attack_move is not None:
        return attack_move
    
    # 2. Kiểm tra nước chặn bắt buộc
    block_move = find_block_move(board, player)
    if block_move is not None:
        return block_move

    # 3. Dùng Minimax khi không có nước đặc biệt
    _, move = minimax_ab(board, depth, -float("inf"), float("inf"), True, player)
    if move is None:
        moves = generate_legal_moves(board)
        if moves:
            return moves[0]
    return move

# ================== CLASS CARO AI ==================

class CaroAI:
    """AI chơi cờ Caro với 3 mức độ khó."""
    
    def __init__(self, depth=3):
        """Khởi tạo AI với độ sâu tìm kiếm mặc định."""
        self.depth = depth

    def get_move(self, board, level=1):
        """
        Trả về nước đi tốt nhất cho AI (O).
        
        Args:
            board: Ma trận 15x15 đại diện bàn cờ
            level: 1=Dễ (depth=2), 2=Vừa (depth=3), 3=Khó (depth=4)
        """
        depth = level + 1  # Dễ:2, Vừa:3, Khó:4
        return find_best_move(board, O, depth)

    def find_best_move(self, board, player):
        """Tìm nước đi tốt nhất cho player bất kỳ."""
        return find_best_move(board, player, self.depth)
