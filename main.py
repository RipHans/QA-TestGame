import time
import argparse
from playwright.sync_api import sync_playwright
from parser import parse_message
from model_logic import judge_one, calculate_rtp
from logger import write_log, build_log_line, log_by_mode

def tick(state, parsed):
    state["round_num"] = parsed.get("round_num", 0)
    state["current_bet"] = parsed["bet_per_line"] * parsed["num_of_lines"] * parsed["denom"]
    state["current_balance"] = parsed["balance"]
    state["denom"] = parsed["denom"]

def get_server_pay(state, parsed):
    if parsed["method"] == "START_GAME" and parsed["status"] == "FINISHED":
        return 0.0
    if parsed["method"] == "END_GAME":
        return (parsed["balance"] - state["balance_after_bet"]) / parsed["denom"] 
    return None  


def on_frame(payload):
    parsed = parse_message(payload)
    if parsed == None: return

    tick(state, parsed)

    if parsed["method"] == "START_GAME" and parsed["status"] == "IN_PROGRESS":
        state["balance_after_bet"] = parsed["balance"]
        return
    server_pay = get_server_pay(state, parsed)
    if server_pay is None:
        write_log(f"SKIPPED round={parsed['round_num']} status={parsed['status']}", state["mode"])
        return
    
    parsed["server_pay"] = server_pay
    parsed["is_match"], parsed["model_pay"] = judge_one(parsed)

    state["last_activity"] = time.monotonic()

    if not parsed["is_match"]: state["total_mismatches"] += 1

    message = build_log_line(parsed)
    log_by_mode(state, parsed, message)
    print(message)


def on_ws(ws):
    ws.on("framereceived", on_frame)


def run(args):
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()
        page.on("websocket", on_ws) 
        page.goto("https://gametests.nyc.wf/")

        page.wait_for_timeout(10000)
        state["last_activity"] = time.monotonic()

        page.keyboard.press("Space")
        while state["round_num"] < args.rounds:
            page.keyboard.press("Space")
            page.wait_for_timeout(300)
            elapsed_time = time.monotonic() - state["last_activity"]
            if elapsed_time > 30:
                if state["current_balance"] < state["current_bet"]:
                    print("NO MONEY! Can't dep. Stopping jobs...")
                else:
                    print(f"Something went wrong, server not responding already {elapsed_time} secs. Stopping jobs...")
                break

        page.wait_for_timeout(4000)

        total_win = round((state["current_balance"] - state["start_balance"]))
        total_bet = state["current_bet"] * state["round_num"]
        
        summary = f"\nTotal win: {total_win}$ (denom: {state["denom"]}$)\nRTP: {calculate_rtp(total_win, total_bet)}%\nTotal mismatches: {state["total_mismatches"]} out of {state["round_num"]} rounds"

        write_log(summary, state["mode"])
        print(summary)
        


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Live analyze & write log for TestGame")
    parser.add_argument("-r", "--rounds", type=int, default=100, help="Target round")
    parser.add_argument("-m", "--mismatches", action="store_true", help="Log only mismatches")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Turn off headless mod for browser")
    args = parser.parse_args()

    state = {
        "round_num": 1,
        "denom": 1,
        "last_activity": 0,
        "start_balance": 10000,
        "current_balance": 10000,
        "balance_after_bet": 10000,
        "total_mismatches": 0,
        "current_bet" : 1,
    }
    
    state["mode"] = "mismatches" if args.mismatches else "each"

    run(args)