from typing import list, tuple, dict
performance = dict[str, float]


def evaluate_performance(p: performance) -> float:
    score = 0
    if p["balls"] > 0:
        strike_rate = (p["runs"]/p["balls"]*100)
        score += p["runs"]*1.5 + strike_rate*0.5
    if p["overs"] > 0:
        economy = p["given_runs"] / p["overs"]
        score += p["wickets"]*25 - (economy*2)
    return score


def compare_players(players: dict[str, float]) -> list[tuple[str, float]]:
    scores = []
    for name, perf in players.items():
        score = evaluate_performance(perf)
        scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


if __name__ == "__main__":
    players = {
        "dhoni": {"runs": 75, "balls": 50, "wickets": 0, "overs": 0, "given_runs": 0},
        "pujara": {"runs": 30, "balls": 20, "wickets": 2, "overs": 4, "given_runs": 28},
        "kohli": {"runs": 10, "balls": 15, "wickets": 3, "overs": 3, "given_runs": 18},
        "shewag": {"runs": 55, "balls": 40, "wickets": 1, "overs": 2, "given_runs": 20},
    }
    
rank = compare_players(players)
for name,score in rank:
    print(f"{name}:{score:.2f}")
