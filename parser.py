import json

def parse_message(payload):
    parsed = {}
    msg = json.loads(payload)
    payload = msg["payload"]
    parsed["method"] = msg.get("method")

    if parsed["method"] in ( "START_GAME", "END_GAME"):

        features = payload["data"]["features"][0]
        betting_param = payload["data"]["betting_param"]
        spin_result = features["last_step"]["reaction"]["spin_result"]

        parsed["round_num"] = payload["data"]["round"]
        parsed["status"] = payload["data"]["status"]
        parsed["balance"] = float(payload["balance"]["balance"])
        parsed["denom"] = float(betting_param["denom"])
        parsed["num_of_lines"] = betting_param["num_of_lines"]
        parsed["bet_per_line"] = betting_param["bet_per_line"]
        parsed["drum"] = spin_result["drum"]
        parsed["server_pay"] = features["current_win"]
    else: return

    return parsed
