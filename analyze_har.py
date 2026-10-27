from model_logic import play_spin
import json

TOLERANCE = 0.0001


def get_messages_from_har():
    messages_list = []
    with open("session.har", encoding="utf-8") as f:

        text = f.read()
        har = json.loads(text)
        entries = har["log"]["entries"]
        for entry in entries:
            soc_messages = entry.get("_webSocketMessages", [])
            for m in soc_messages:
                if m["type"] == "receive":
                    data = json.loads(m["data"])
                    messages_list.append(data)
    return messages_list


def get_spins_data(mess_list):
    spins = []
    for m in mess_list:
        clean_spin = {}
        
        method = m["method"]
        payload = m["payload"]
        betting_param = None
        features = None

        clean_spin["method"] = m["method"]

        if method == "START_GAME" or method == "END_GAME":
            betting_param = payload["data"]["betting_param"]
            features = payload["data"]["features"][0]
            clean_spin["round"] = payload["data"]["round"]
            clean_spin["balance"] = float(payload["balance"]["balance"])
        else: continue

        spin_result = features["last_step"]["reaction"]["spin_result"]
        clean_spin["bet_per_line"] = betting_param["bet_per_line"]
        clean_spin["denom"] = float(betting_param["denom"])
        clean_spin["num_of_lines"] = betting_param["num_of_lines"]
        clean_spin["drum"] = spin_result["drum"]
        clean_spin["current_win"] = features["current_win"]
        
        spins.append(clean_spin)

    return spins

       
def get_gummed_spins(spins):
    gummed_spins = {}         # Gummed spins (START_GAME + END_GAME = 1 record)
    for s in spins:
        round_num = s["round"]
        if s["method"] == "START_GAME":
            gummed_spins[round_num] = {}
            gummed_spins[round_num]["method"] = s["method"]
            gummed_spins[round_num]["bet_per_line"] = s["bet_per_line"]
            gummed_spins[round_num]["denom"] = s["denom"]
            gummed_spins[round_num]["num_of_lines"] = s["num_of_lines"]
            gummed_spins[round_num]["drum"] = s["drum"]
            gummed_spins[round_num]["balance"] = s["balance"]
            gummed_spins[round_num]["server_pay"] = 0.0
        elif s["method"] == "END_GAME" and round_num not in gummed_spins: continue  
        else:
            gummed_spins[round_num]["method"] = s["method"]
            gummed_spins[round_num]["server_pay"] = (s["balance"] - gummed_spins[round_num]["balance"]) / s["denom"]
            gummed_spins[round_num]["balance"] = s["balance"]

    return gummed_spins


messages_list = get_messages_from_har()
spins_data = get_spins_data(messages_list)
gummed_spins = get_gummed_spins(spins_data)


def analize(spins):
    sinners = {}
    first, last = next(iter(spins)), next(reversed(spins))
    print(f"TOTAL ROUNDS: {len(spins)}\t FIRST: {first}, LAST {last}\n")
    print(f"{"ROUND":<8}{"BALANCE":<12}{"BET":<8}{"SERVER PAY":<12}{"MODEL PAY":<12}{"RESULT":<10}")
    for s in spins:
        model_pay = play_spin(spins[s])
        server_pay = spins[s]["server_pay"]
        balance = spins[s]["balance"]
        bet = f"{spins[s]["bet_per_line"]:g}x{spins[s]["num_of_lines"]}"
        if abs(model_pay - server_pay) < TOLERANCE:
            print(f"{s:<8}{balance:<12}{bet:<8}{server_pay:<12}{model_pay:<12}{"OK":<10}")
        else:
            sinners[s] = {}
            sinners[s]["drum"] = spins[s]["drum"]
            sinners[s]["server_pay"] = server_pay
            sinners[s]["model_pay"] = model_pay
            print(f"{s:<8}{balance:<12}{bet:<8}{server_pay:<12}{model_pay:<12}{"MISMATCH":<10}")

    print(f"\nLIST OF MISMATCHES: {len(sinners)}\n")
    print(f"{"ROUND":<8}{"SERVER PAY":<19}{"MODEL PAY":<11}PROOF\n")
    for s in sinners:
        print(f"№ {s:<8}x: {sinners[s]["server_pay"]:<14}v: {sinners[s]["model_pay"]:<8}{sinners[s]["drum"]}")


if __name__ == "__main__":
    analize(gummed_spins)