import random

# This is an out-of-the-box ghost AI implementation.  In theory this is
# pluggable from a front-end, but that isn't necessary.  Note that the ghost is
# assumed to be outside of the ghost box for ghost logic functions.


def simple_logic(board, location, state):
    directions = board.allowable_directions(location, True)

    # if going in a direction with more space, keep going
    if state["current_direction"]:
        limit = directions[state["current_direction"]]
        distance = (location - limit).manhattan()
        if distance > board.WALL_BUMPER:
            return state["current_direction"]

    choices = []
    for kdir, limit in directions.items():
        distance = (location - limit).manhattan()

        if distance > board.WALL_BUMPER:
            choices.append(kdir)

    newdir = random.choose(choices)
    state["current_direction"] = newdir
    return newdir
