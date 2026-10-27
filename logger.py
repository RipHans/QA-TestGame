from pathlib import Path
from datetime import datetime

folder = Path("attachments/logs")


def get_current_date_time():
    now = datetime.now()
    return now.strftime("%d-%m-%Y_%H-%M-%S")

session = get_current_date_time()

def build_log_line(parsed):
    return f"{get_current_date_time():<20} | {"OK" if parsed["is_match"] else "MISMATCH":<8} | round={parsed["round_num"]:<4} | bet={parsed["bet_per_line"]}x{parsed["num_of_lines"]:<5} | server={parsed["server_pay"]:<5} | model={parsed.get("model_pay", ""):<5} | drum={parsed["drum"]}"

def log_by_mode(state, parsed, message):
    if state["mode"] == "each":
        write_log(message, state["mode"])
    else:
        if not parsed["is_match"]:
            write_log(message, state["mode"])

def write_log(message, mode):
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"log-{mode}_session-{session}.txt"
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(message + "\n")