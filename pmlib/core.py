import time
import random
from . import maps
from . import ghost_ootb


class Character:
    def __init__(self):
        self.location = None
        self.state = {}

        self.logic = None


class PacmanBoard:
    # fraction of a cell
    # paku & ghost collide with-in this distance
    COLLISION_CLOSE = 0.4
    # can corner inside this tolerance and actual location will be pushed on
    # track
    CORNER_CORRECT = 0.15
    # this is the minimal amount to a corner by an AI
    WALL_BUMPER = 0.03
    # when a location is with-in epsilon of a path, it is considered on the
    # path; this is basically a floating point accomodation
    EPSILON = 0.0001

    # ** A note on character speed **
    # My recollection suggests that a Pacman character should take about 2
    # seconds to cross the board horizontally.  This is moving about 20 cells
    # every 2 seconds or 1 cell in 0.1 seconds.  The game loop iteration
    # cadence combined with the move-per-iteration distance governs this net
    # speed.  The appearance of fluid movement is only acheived by preferring a
    # small move-per-iteration and keeping the cadence high (or interval
    # short).

    # per above note: want 10 cells/sec = MOVE_DISTANCE / LOOP_SLEEP_SECONDS
    # this is the movement amount of each iteration
    MOVE_DISTANCE = 0.08
    LOOP_SLEEP_SECONDS = 0.008

    #  Fickle, Chaser, Ambusher and Stupid
    #  Inky, Blinky, Pinky and Clyde
    GHOST_COUNT = 4

    def __init__(self):
        self.map = None

        self.cookies = []
        self.pills = []

        self.retries = 3
        self.empowered = False

        self.paku = None
        self.ghosts = None

    def load_from_string(self, s):
        self.map = maps.PacmanMap.from_str(s)

        self.paku = Character()

        glogic = ghost_ootb.simple_logic
        self.ghosts = [Character(logic=glogic) for _ in range(self.GHOST_COUNT)]

        # record cookie and pill locations
        self.cookies = self.map.cookie_locations()
        self.pills = self.map.pill_locations()

        # record paku & ghost points
        self.reset_characters()

    def is_cleared(self):
        return len(self.cookies) > 0

    @classmethod
    def is_close(cls, loc1, loc2):
        return (loc1 - loc2).manhattan() < cls.COLLISION_CLOSE

    def wall_limit_from(self, loc, direction):
        walls = self.map.WALL

        current = loc.rounded()
        assert self.map.get[current] & walls == 0, "cannot go any direction _in_ a wall"

        delta = loc - current

        limit = None

        # If with-in CORNER_CORRECT perpendicular to direction then no need
        # to check contact with diagonal cell, in that case the character
        # motion code will first center on the perpendicular travel route.

        if direction[0] == 0 and abs(delta[0]) > self.CORNER_CORRECT:
            delta1 = 1 if delta[0] > 0 else -1
            diagonal = current + (delta1, direction[1])
            if self.map[diagonal] & walls:
                limit = current + direction
        if direction[1] == 0 and abs(delta[1]) > self.CORNER_CORRECT:
            delta1 = 1 if delta[1] > 0 else -1
            diagonal = current + (direction[0], delta1)
            if self.map[diagonal] & walls:
                limit = current + direction

        if limit is None:
            step = current
            while True:
                step = step + direction
                if self.map[step] & walls:
                    limit = step
                    break

        return limit

    def allowable_directions(self, loc, as_ghost):
        # TODO: re-use wall_limit_from

        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]

        walls = self.map.WALL | (self.map.GATE if not as_ghost else 0)

        current = loc.rounded()
        assert self.map.get[current] & walls == 0, "cannot go any direction _in_ a wall"

        delta = loc - current

        results = {}

        for direction in dirs:
            limit = None

            # If with-in CORNER_CORRECT perpendicular to direction then no need
            # to check contact with diagonal cell, in that case the character
            # motion code will first center on the perpendicular travel route.

            if direction[0] == 0 and abs(delta[0]) > self.CORNER_CORRECT:
                delta1 = 1 if delta[0] > 0 else -1
                diagonal = current + (delta1, direction[1])
                if self.map[diagonal] & walls:
                    limit = current + direction
            if direction[1] == 0 and abs(delta[1]) > self.CORNER_CORRECT:
                delta1 = 1 if delta[1] > 0 else -1
                diagonal = current + (direction[0], delta1)
                if self.map[diagonal] & walls:
                    limit = current + direction

            if limit is None:
                step = current
                while True:
                    step = step + direction
                    if self.map[step] & walls:
                        limit = step
                        break

            # compare to limit
            results[direction] = limit

        return results

    def navigate(self, location, direction):
        # TODO:  many ill-defined elements here
        # TODO:  must support wrap-around
        offset = self.max_parallel(direction, self.MOVE_DISTANCE)

        off_axis = direction.perpendicular()
        axis = direction.parallel()

        near = location.rounded()
        delta = location - near

        if abs(delta.x) < self.EPSILON and abs(delta.y) < self.EPSILON:
            return location.on_axis(off_axis) + offset
        elif delta.is_on_axis(axis):
            # offset should not be larger than delta
            return location + offset
        else:
            # first, complete to corner
            offset = self.max_parallel(delta, self.MOVE_DISTANCE)
            return location + offset

    def follow_breadcrumbs(self, current, breadcrumbs):
        assert len(breadcrumbs) >= 1

        new_loc = self.navigate(current, breadcrumbs[0])
        if self.is_close(new_loc, breadcrumbs[0]):
            breadcrumbs = breadcrumbs[1:]

        return new_loc, breadcrumbs

    def is_collided(self):
        ploc = self.paku.location
        return any(self.is_close(ploc, ghost.location) for ghost in self.ghosts)

    def _move_character(self, character, direction):
        # TODO:  this appears to be redundant with navigate

        # TODO implement centering before turning logic (which means we may go
        # perpendicular to direction prior to going that way); we never go two
        # directions in one turn.  a character may lose a fragment of cadence
        # in a turn

        limit = self.wall_limit_from(character.location, direction)

        distance = self.MOVE_DISTANCE
        if (limit - character.location).manhattan() < self.MOVE_DISTANCE:
            distance = (limit - character.location).manhattan()

        character.location += maps.Location(
            distance * direction[0], distance * direction[1]
        )

    def play_paku(self):
        dir_togo = self.paku.logic(self, self.paku.location, self.paku.state)

        self._move_character(self.paku, dir_togo)

        self.consume_cookie(self.paku.location)
        self.consume_pill(self.paku.location)

    def play_ghost(self, ghost):
        # Note that ghost unhoming shall be prepared in rehome_ghost

        # TODO:  does a logic function really just return breadcrumbs

        if ghost.breadcrumbs and ghost.breadcrumbs[0][0] == "recompute":
            dir_togo = ghost.logic(self, ghost.location, ghost.state)

        if ghost.breadcrumbs:
            new_loc, bc = self.follow_breadcrumbs(ghost.location, ghost.breadcrumbs)

            ghost.location = new_loc

            ghost.breadcrumbs = bc

        dir_togo = ghost.logic(self, ghost.location, ghost.state)

        self._move_character(ghost, dir_togo)

    def rehome_ghost(self, ghost):
        def random_between(l1, l2):
            assert (l1 - l2).manhattan() == 1

            offset = random.random()
            delta = l1 - l2

            return l1 + maps.Location(offset * delta[0], offset * delta[1])

        pairs = []
        ghlocs = [maps.Location(*g) for g in self.map.ghost_locations()]
        for gloc1 in ghlocs:
            for gloc2 in ghlocs:
                if (gloc1 - gloc2).manhattan() == 1:
                    pairs.append(gloc1, gloc2)

        ghost.location = random_between(*random.choose(pairs))
        # TODO: implement ghost unhoming by means of setting the breadcrumb property

    def reset_characters(self):
        for ghost in self.ghosts:
            self.rehome_ghost(ghost)

        self.paku.location = maps.Location(*self.map.paku_location())


def play(board, render, music):
    render(board)

    while True:
        board.play_paku()
        for ghost in board.ghosts:
            board.play_ghost(ghost)

        if board.is_cleared():
            render(board)
            music.happy()
            return True

        if board.empowered:
            for ghost in board.ghosts:
                if board.is_close(board.paku.location, ghost.location):
                    board.rehome_ghost(ghost)

        render(board)

        if not board.empowered and board.is_collided():
            if board.retries > 0:
                music.sad()
                board.reset_characters()
                board.retries -= 1
            else:
                music.devastated()
                return False

        # So the assumption is that the rest of this loop takes 0 time :)
        time.sleep(board.LOOP_SLEEP_SECONDS)
