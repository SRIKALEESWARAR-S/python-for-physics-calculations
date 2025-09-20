import random

class cricket_game:
    def __init__(self, teams: tuple[str, str]):
        if len(teams) != 2:
            raise ValueError("You must have two teams to play")
        self.teams = teams
        self.scores: dict[str, int] = {team: 0 for team in teams}
        self.wickets: dict[str, int] = {team: 0 for team in teams}
        self.balls_played: dict[str, int] = {team: 0 for team in teams}
        self.overs = 5
        self.balls_per_over = 6

    def play_ball(self, team: str):
        if self.balls_played[team] >= self.overs * self.balls_per_over or self.wickets[team] >= 10:
            raise ValueError(f"Innings over for {team}")

        outcome = random.choices(
            population=[1, 2, 3, 4, 5, 6, 'w'],
            weights=[0.3, 0.25, 0.15, 0.05, 0.1, 0.1, 0.05],
            k=1
        )[0]

        if outcome == 'w':
            self.wickets[team] += 1
        else:
            self.scores[team] += outcome

        self.balls_played[team] += 1

    def play_innings(self, team: str) -> None:
        print(f"\nStarting innings for {team}")
        try:
            while self.balls_played[team] < self.overs * self.balls_per_over and self.wickets[team] < 10:
                self.play_ball(team)
                print(f"Ball {self.balls_played[team]}: score = {self.scores[team]}, wickets = {self.wickets[team]}")
        except ValueError as ve:
            print(ve)

        print(f"Innings finished for {team} with score {self.scores[team]} for {self.wickets[team]} wickets")

    def start_match(self) -> None:
        self.play_innings(self.teams[0])
        self.play_innings(self.teams[1])

        score1 = self.scores[self.teams[0]]
        score2 = self.scores[self.teams[1]]

        print(f"\nFinal scores:\n{self.teams[0]}: {score1}\n{self.teams[1]}: {score2}")

        if score1 > score2:
            print(f"{self.teams[0]} wins!")
        elif score2 > score1:
            print(f"{self.teams[1]} wins!")
        else:
            print("Match drawn")


# Example run
teams = ("New Zealand", "Scotland")
game = cricket_game(teams)
game.start_match()
