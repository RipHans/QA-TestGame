import pytest
from model_logic import play_spin

''' TEST DATA '''

CASES = [
    {"name": "no win",
     "drum": [[5, 5, 5], [7, 2, 8], [6, 4, 4]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 0},
    {"name": "pair on the left pays (2 lemons, line 2)",
     "drum": [[5, 6, 7], [5, 8, 6], [6, 2, 4]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 30},
    {"name": "three of a kind pays (3 lemons, line 2)",
     "drum": [[5, 6, 7], [5, 8, 6], [5, 2, 4]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 40},
    {"name": "pair on the right (rules say it pays, real game paid 0)",
     "drum": [[7, 2, 7], [4, 4, 2], [8, 1, 4]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 30},
    {"name": "same symbol not adjacent (5-7-5) pays nothing",
     "drum": [[1, 5, 2], [3, 7, 4], [6, 5, 8]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 0},
    {"name": "two winning lines are added up",
     "drum": [[5, 3, 7], [5, 4, 7], [1, 6, 2]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 60},
    {"name": "bet_per_line 2 doubles win and bet",
     "drum": [[5, 6, 7], [5, 8, 6], [6, 2, 4]], "num_of_lines": 5, "bet_per_line": 2,
     "want_win": 60},
    {"name": "win on a disabled line is not paid (1 line enabled)",
     "drum": [[5, 6, 7], [5, 8, 6], [6, 2, 4]], "num_of_lines": 1, "bet_per_line": 1,
     "want_win": 0},
    {"name": "all_grapes",
     "drum": [[4, 4, 4], [4, 4, 4], [4, 4, 4]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 400},
    {"name": "all_cherryes",
     "drum": [[6, 6, 6], [6, 6, 6], [6, 6, 6]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 400},
    {"name": "all_plums",
     "drum": [[7, 7, 7], [7, 7, 7], [7, 7, 7]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 400},
    {"name": "all_lemons",
     "drum": [[5, 5, 5], [5, 5, 5], [5, 5, 5]], "num_of_lines": 5, "bet_per_line": 1,
     "want_win": 200},
     
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_round(case):
    model_pay = play_spin(case)
    assert model_pay == case["want_win"]