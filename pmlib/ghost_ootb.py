import random

# This is an out-of-the-box ghost AI implementation.  In theory this is
# pluggable from a front-end, but that isn't necessary.


def simple_logic(board, location, state):
    directions = board.allowable_directions(location, True)

    # TODO:  look for the gate out of ghost home.

    # if going in a direction with more space, keep going
    if state["current_direction"]:
        limit = directions[state["current_direction"]]
        distance = (location - limit).size()
        if distance > board.WALL_BUMPER:
            return state["current_direction"]

    choices = []
    for kdir, limit in directions.items():
        distance = (location - limit).size()

        if distance > board.WALL_BUMPER:
            choices.append(kdir)

    newdir = random.choose(choices)
    state["current_direction"] = newdir
    return newdir
