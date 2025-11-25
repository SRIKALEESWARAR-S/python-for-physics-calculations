Fail = []

def pour_problem(X, Y, goal, start=(0, 0)):
    """Solve the water pouring problem.

    X, Y: capacities of the two glasses
    goal: desired amount of water in either glass
    start: starting state (default (0, 0))
    Returns a path: [start, action1, state1, action2, state2, ...]
    """

    if goal in start:
        return [start]

    explored = set()       # set of states we have visited
    frontier = [[start]]   # ordered list of paths

    while frontier:
        path = frontier.pop(0)
        (x, y) = path[-1]
        for (state, action) in successors(x, y, X, Y).items():
            if state in explored:
                continue
            explored.add(state)
            path2 = path + [action, state]
            if goal in state:
                return path2
            else:
                frontier.append(path2)

    return Fail


def successors(x, y, X, Y):
    """Return a dict of {state: action} reachable from (x, y)."""

    assert x <= X and y <= Y

    return {
        # pour from X to Y
        ((0, x + y) if x + y <= Y else (x - (Y - y), Y)): 'x->y',

        # pour from Y to X
        ((x + y, 0) if x + y <= X else (X, y - (X - x))): 'y->x',

        # fill X
        (X, y): 'fill X',

        # fill Y
        (x, Y): 'fill Y',

        # empty X
        (0, y): 'empty X',

        # empty Y
        (x, 0): 'empty Y',
    }


# Example usage:
if __name__ == "__main__":
    capacityX = 4
    capacityY = 9
    goal_amount = 6
    result = pour_problem(capacityX, capacityY, goal_amount)
    if result:
        print("Path to reach the goal:")
        for step in result:
            print(step)
    else:
        print("No solution found.")