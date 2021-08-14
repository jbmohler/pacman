import random
from . import maps
from . import ghost_ootb


class Location:
    def __init__(self, x=None, y=None):
        """
        >>> loc = Location(1, 2)
        >>> loc.x == loc[0]
        True
        >>> loc.x
        1
        """
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Location({self.x}, {self.y})"

    def __len__(self):
        # we masquerade as a tuple
        return 2

    def __getitem__(self, index):
        assert type(index) is int and 0 <= index <= 1
        return self.x if index == 0 else self.y

    def manhattan(self):
        """
        Return the manhattan size (sum of legs of right triangle with
        hypotenuse from origin to this point) rather than the distance from the
        origin.   It's simple and good enough and keeps ints as ints.

        >>> loc = Location(1.5, 3.)
        >>> loc.manhattan()
        4.5
        >>> loc = Location(1, 3)
        >>> loc.manhattan(), type(loc.manhattan())
        (4, int)
        """

        return abs(self.x) + abs(self.y)

    def __add__(self, other):
        """
        >>> l1 = Location(1, 2)
        >>> l2 = Location(3, 4)
        >>> l1 + (5, 6)
        Location(6, 8)
        >>> l1 + l2
        Location(4, 6)
        """

        return Location(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        return Location(self.x - other[0], self.y - other[1])


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

    # this is the movement amount of each iteration
    MOVE_DISTANCE = 0.08

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

    def is_collided(self):
        ploc = self.paku.location
        return any(self.is_close(ploc, ghost.location) for ghost in self.ghosts)

    def _move_character(self, character, direction):
        # TODO implement centering before turning logic (which means we may go
        # perpendicular to direction prior to going that way); we never go two
        # directions in one turn.  a character may lose a fragment of cadence
        # in a turn

        limit = self.wall_limit_from(character.location, direction)

        distance = self.MOVE_DISTANCE
        if (limit - character.location).manhattan() < self.MOVE_DISTANCE:
            distance = (limit - character.location).manhattan()

        character.location += Location(distance * direction[0], distance * direction[1])

    def play_paku(self):
        dir_togo = self.paku.logic(self, self.paku.location, self.paku.state)

        self._move_character(self.paku, dir_togo)

        self.consume_cookie(self.paku.location)
        self.consume_pill(self.paku.location)

    def play_ghost(self, ghost):
        # We move the ghost out of the ghost box here; that is not pluggable logic.

        # TODO: implement ghost unhoming

        dir_togo = ghost.logic(self, ghost.location, ghost.state)

        self._move_character(ghost, dir_togo)

    def rehome_ghost(self, ghost):
        def random_between(l1, l2):
            assert (l1 - l2).manhattan() == 1

            offset = random.random()
            delta = l1 - l2

            return l1 + Location(offset * delta[0], offset * delta[1])

        pairs = []
        ghlocs = [Location(*g) for g in self.map.ghost_locations()]
        for gloc1 in ghlocs:
            for gloc2 in ghlocs:
                if (gloc1 - gloc2).manhattan() == 1:
                    pairs.append(gloc1, gloc2)

        ghost.location = random_between(*random.choose(pairs))

    def reset_characters(self):
        for ghost in self.ghosts:
            self.rehome_ghost(ghost)

        self.paku.location = Location(*self.map.paku_location())


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
