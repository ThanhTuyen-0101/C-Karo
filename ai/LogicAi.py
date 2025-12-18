# ================== Háº°NG Sá» VÃ€ HÆ¯á»šNG ÄI ==================

SIZE  = 15      # KÃ­ch thÆ°á»›c bÃ n cá» 15x15
EMPTY = 0       # Ã” trá»‘ng
X     = 1       # Quân X (ngu?i)
O     = -1      # Quân O (AI)
# 4 hÆ°á»›ng chÃ­nh: ngang, dá»c, chÃ©o xuá»‘ng pháº£i, chÃ©o xuá»‘ng trÃ¡i
DIRECTIONS = [
    (0, 1),
    (1, 0),
    (1, 1),
    (1, -1),
]


# ================== HÃ€M TIá»†N ÃCH CÆ  Báº¢N ==================

def in_board(r, c):
    """Kiá»ƒm tra (r, c) cÃ³ náº±m trong bÃ n cá» hay khÃ´ng."""
    return 0 <= r < SIZE and 0 <= c < SIZE


def get_opponent(player):
    """Tráº£ vá» quÃ¢n Ä‘á»‘i thá»§ cá»§a player."""
    return X if player == O else O


# ================== HÃ€M SINH NÆ¯á»šC ÄI Há»¢P Lá»† (Æ¯U TIÃŠN Gáº¦N NGÆ¯á»œI) ==================

def generate_legal_moves(board, radius=4):
    """
    Sinh danh sÃ¡ch cÃ¡c nÆ°á»›c Ä‘i há»£p lá»‡ (r, c).

    - Chá»‰ sinh cÃ¡c Ã´ trá»‘ng náº±m trong vÃ¹ng bao quanh táº¥t cáº£ quÃ¢n Ä‘Ã£ Ä‘Ã¡nh,
      ná»›i thÃªm 'radius' Ã´.
    - BÃ n trá»‘ng -> má»i Ã´ trá»‘ng Ä‘á»u há»£p lá»‡.
    - Sáº¯p xáº¿p moves: Æ°u tiÃªn nÆ°á»›c Ä‘i gáº§n QUÃ‚N NGÆ¯á»œI chÆ¡i (X) trÆ°á»›c,
      Ä‘á»ƒ AI dá»… cháº·n hÆ¡n.
    """
    size = len(board)
    has_stone = False
    min_r, max_r = size, -1
    min_c, max_c = size, -1

    # TÃ¬m bounding box chá»©a táº¥t cáº£ quÃ¢n
    for r in range(size):
        for c in range(size):
            if board[r][c] != EMPTY:
                has_stone = True
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)

    moves = []

    # BÃ n trá»‘ng -> cho phÃ©p má»i Ã´ trá»‘ng
    if not has_stone:
        for r in range(size):
            for c in range(size):
                if board[r][c] == EMPTY:
                    moves.append((r, c))
        return moves

    # Má»Ÿ rá»™ng vÃ¹ng quanh quÃ¢n Ä‘Ã£ Ä‘Ã¡nh
    min_r = max(0, min_r - radius)
    max_r = min(size - 1, max_r + radius)
    min_c = max(0, min_c - radius)
    max_c = min(size - 1, max_c + radius)

    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            if board[r][c] == EMPTY:
                moves.append((r, c))

    # --- Æ¯U TIÃŠN Gáº¦N QUÃ‚N NGÆ¯á»œI (X) ---
    opp_cells = [(r, c) for r in range(size) for c in range(size)
                 if board[r][c] == X]

    if opp_cells:
        def dist_to_opp(m):
            r, c = m
            return min(abs(r - orr) + abs(c - occ) for orr, occ in opp_cells)
        moves.sort(key=dist_to_opp)
    else:
        # náº¿u chÆ°a cÃ³ quÃ¢n ngÆ°á»i -> Æ°u tiÃªn gáº§n trung tÃ¢m
        center = SIZE // 2
        moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))

    return moves


# ================== HÃ€M CHECK THáº®NG (ÄÃšNG 5 QUÃ‚N) ==================

def is_exact_five(board, r, c, dr, dc):
    """
    Kiá»ƒm tra táº¡i Ã´ (r, c) theo hÆ°á»›ng (dr, dc) cÃ³ ÄÃšNG 5 quÃ¢n liÃªn tiáº¿p khÃ´ng.
    - KhÃ´ng tÃ­nh chuá»—i dÃ i hÆ¡n 5 (overline).
    - (r, c) pháº£i lÃ  Ã´ Äáº¦U chuá»—i.
    """
    player = board[r][c]
    if player == EMPTY:
        return False

    pr, pc = r - dr, c - dc
    if in_board(pr, pc) and board[pr][pc] == player:
        return False

    cnt = 0
    cr, cc = r, c
    while in_board(cr, cc) and board[cr][cc] == player and cnt <= 5:
        cnt += 1
        cr += dr
        cc += dc

    if cnt != 5:
        return False

    if in_board(cr, cc) and board[cr][cc] == player:
        return False

    return True


def check_winner(board):
    """Tráº£ vá» X hoáº·c O náº¿u cÃ³ ngÆ°á»i tháº¯ng, None náº¿u chÆ°a."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] in (X, O):
                for dr, dc in DIRECTIONS:
                    if is_exact_five(board, r, c, dr, dc):
                        return board[r][c]
    return None


# ================== HÃ€M ÄÃNH GIÃ (HEURISTIC) ==================

def count_sequence(board, r, c, dr, dc, player):
    """Äáº¿m Ä‘á»™ dÃ i chuá»—i liÃªn tiáº¿p báº¯t Ä‘áº§u táº¡i (r,c) theo hÆ°á»›ng (dr,dc)."""
    length = 0
    cr, cc = r, c
    while in_board(cr, cc) and board[cr][cc] == player:
        length += 1
        cr += dr
        cc += dc
    return length


def evaluate(board, player):
    """
    ÄÃ¡nh giÃ¡ tráº¡ng thÃ¡i bÃ n cá» cho player.

    - Chuá»—i 2: 10
    - Chuá»—i 3: 50
    - Chuá»—i 4: 200
    - score = my_score - 3 * opp_score  (phÃ²ng thá»§ máº¡nh)
    """
    opponent = get_opponent(player)

    def score_for(p):
        total = 0
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == p:
                    for dr, dc in DIRECTIONS:
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


# ================== HÃ€M TÃŒM NÆ¯á»šC CHáº¶N Báº®T BUá»˜C ==================

def find_block_move(board, player):
    """
    TÃ¬m nÆ°á»›c Ä‘i CHáº¶N Ä‘á»‘i thá»§.
    Æ¯u tiÃªn:
    1) Cháº·n cÃ¡c Ã´ mÃ  Ä‘á»‘i thá»§ cÃ³ thá»ƒ táº¡o chuá»—i >= 4.
    2) Náº¿u khÃ´ng cÃ³, cháº·n cÃ¡c Ã´ mÃ  Ä‘á»‘i thá»§ táº¡o Ä‘Æ°á»£c chuá»—i = 3.
    """
    opponent = get_opponent(player)
    size = len(board)

    block_four = None
    block_three = None

    for r in range(size):
        for c in range(size):
            if board[r][c] != EMPTY:
                continue

            board[r][c] = opponent

            max_len = 1
            for dr, dc in DIRECTIONS:
                length = 1
                cr, cc = r + dr, c + dc
                while in_board(cr, cc) and board[cr][cc] == opponent:
                    length += 1
                    cr += dr
                    cc += dc
                cr, cc = r - dr, c - dc
                while in_board(cr, cc) and board[cr][cc] == opponent:
                    length += 1
                    cr -= dr
                    cc -= dc

                if length > max_len:
                    max_len = length

            board[r][c] = EMPTY

            if max_len >= 4:
                return (r, c)      # cháº·n chuá»—i 4+ -> Æ°u tiÃªn cao nháº¥t
            elif max_len == 3 and block_three is None:
                block_three = (r, c)

    if block_three is not None:
        return block_three

    return None


# ================== HÃ€M TÃŒM NÆ¯á»šC Táº¤N CÃ”NG Báº®T BUá»˜C ==================

def find_attack_move(board, player):
    """
    TÃ¬m nÆ°á»›c Ä‘i Táº¤N CÃ”NG cho player (AI):
    Chá»‰ Æ°u tiÃªn cÃ¡c nÆ°á»›c ÄÃNH VÃ€O LÃ€ THáº®NG NGAY (chuá»—i >=5).
    KhÃ´ng Æ°u tiÃªn riÃªng cho 3 -> 4.
    """
    size = len(board)

    for r in range(size):
        for c in range(size):
            if board[r][c] != EMPTY:
                continue

            # Giáº£ láº­p player Ä‘Ã¡nh vÃ o (r, c)
            board[r][c] = player

            max_len = 1
            for dr, dc in DIRECTIONS:
                length = 1
                cr, cc = r + dr, c + dc
                while in_board(cr, cc) and board[cr][cc] == player:
                    length += 1
                    cr += dr
                    cc += dc
                cr, cc = r - dr, c - dc
                while in_board(cr, cc) and board[cr][cc] == player:
                    length += 1
                    cr -= dr
                    cc -= dc

                if length > max_len:
                    max_len = length

            board[r][c] = EMPTY  # hoÃ n tÃ¡c

            if max_len >= 5:
                # ÄÃ¡nh vÃ o lÃ  cÃ³ chuá»—i 5+ -> chá»n ngay
                return (r, c)

    # KhÃ´ng cÃ³ nÆ°á»›c tháº¯ng ngay
    return None



# ================== MINIMAX + ALPHAâ€“BETA PRUNING ==================

def minimax_ab(board, depth, alpha, beta, maximizing, player):
    """Minimax cÃ³ cáº¯t tá»‰a alphaâ€“beta, tráº£ vá» (giÃ¡ trá»‹, nÆ°á»›c Ä‘i tá»‘t nháº¥t)."""
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


# ================== HÃ€M CHá»ŒN NÆ¯á»šC ÄI CUá»I CÃ™NG ==================

def find_best_move(board, player, depth=3):
    """
    Thá»© tá»± Æ°u tiÃªn:
    1) NÆ°á»›c Táº¤N CÃ”NG (tháº¯ng ngay hoáº·c táº¡o chuá»—i 4).
    2) NÆ°á»›c CHáº¶N (chuá»—i 4, rá»“i chuá»—i 3 cá»§a Ä‘á»‘i thá»§).
    3) Minimax + Alphaâ€“Beta.
    """


    attack_move = find_attack_move(board, player)
    if attack_move is not None:
        return attack_move
    
    block_move = find_block_move(board, player)
    if block_move is not None:
        return block_move

    # 3. KhÃ´ng cÃ³ táº¥n cÃ´ng/cháº·n Ä‘áº·c biá»‡t, dÃ¹ng minimax
    _, move = minimax_ab(board, depth, -float("inf"), float("inf"), True, player)
    if move is None:
        moves = generate_legal_moves(board)
        if moves:
            return moves[0]
    return move



class CaroAI:
    def __init__(self, depth=3):
        self.depth = depth

    def get_move(self, board, level=1):
        # Dễ: depth=2, Vừa: depth=3, Khó: depth=4
        depth = level + 1
        return find_best_move(board, -1, depth)

    def find_best_move(self, board, player):
        return find_best_move(board, player, self.depth)
