# SYMBOL ID: {3 одинаковых: выплата, 2 одинаковых: выплата}
PAYTABLE = {
    1: {3: 750, 2: 550},        # SEVEN
    2: {3: 200, 2: 100},        # STAR
    3: {3: 60, 2: 50},          # BELL 2: 60 in interface
    4: {3: 40, 2: 30},          # GRAPE 3: 60 in interface
    5: {3: 40, 2: 30},          # LEMON
    6: {3: 40, 2: 30},          # CHERRY
    7: {3: 40, 2: 30},          # PLUM
    8: {3: 5, 2: 3},            # BAR
}
 
# PAYLINES: номер линии: строка выплаты (0 верх, 1 середина, 2 низ) на каждом барабане
LINES = {
    1: (1, 1, 1),
    2: (0, 0, 0),
    3: (2, 2, 2),
    4: (0, 1, 2),
    5: (2, 1, 0)
}
 
''' MAIN LOGIC '''
def get_symbols_on_line(reels, idx):
    return [reels[col][row] for col, row in enumerate(idx)]
 
 
def get_all_lines(reels):
    return [get_symbols_on_line(reels, idx) for idx in LINES.values()]
 
 
def search_for_win_combos(lines, selected):
    combos = []
    for line in lines[:selected]:
        if len(set(line)) == 1:
            combos.append([line[0], 3])  # [symbol_id, count]
        elif line[0] == line[1]:
            combos.append([line[0], 2])
        elif line[2] == line[1]:
            combos.append([line[1], 2])
    return combos
 
 
def calculate_win(combos, case):
    win_pay = 0
    symb_set = set([symb for reel in case["drum"] for symb in reel])
    symb = tuple(symb_set)[0]
    if len(symb_set) == 1 and symb in {4, 6, 7}:
        return PAYTABLE[symb][3] * case["num_of_lines"] * case["bet_per_line"] * 2
    for symb_id, best_match in combos:
        win_pay += PAYTABLE[symb_id][best_match] * case["bet_per_line"]
    return win_pay
 
 
def update_credit_balance(last_credit_balance, bet_per_line, selected_lines, dirty_winnings):
    return last_credit_balance - bet_per_line * selected_lines + dirty_winnings


def play_spin(case):
    all_lines = get_all_lines(case["drum"])
    win_combos = search_for_win_combos(all_lines, case["num_of_lines"])
    model_pay = calculate_win(win_combos, case)
    return float(model_pay)

def judge_one(msg):
    msg["model_pay"] = play_spin(msg)
    msg["is_match"] = True if abs(msg["model_pay"] - msg["server_pay"]) < 0.001 else False
    return msg["is_match"], msg["model_pay"]

def calculate_rtp(total_win, total_bets):
    rtp = (total_win + total_bets) / total_bets * 100
    return round(rtp, 2)