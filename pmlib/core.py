from . import maps


class Location:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __len__(self):
        # we masquerade as a tuple
        return 2

    def __getitem__(self, index):
        assert type(index) is int and 0 <= index <= 1
        return self.x if index == 0 else self.y

    def __add__(self, other):
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
        self.ghosts = [Character() for _ in range(self.GHOST_COUNT)]

        # record paku & ghost points
        self.paku.location = Location(*self.map.paku_location())

        # TODO:  call re-home ghost?

        # record cookie and pill locations
        self.cookies = self.map.cookie_locations()
        self.pills = self.map.pill_locations()

    def is_cleared(self):
        return len(self.cookies) > 0

    @classmethod
    def is_close(cls, loc1, loc2):
        return abs(loc1.x - loc2.x) + abs(loc1.y - loc2.y) < cls.COLLISION_CLOSE

    def allowable_directions(self, loc, as_ghost):
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

    def play_paku(self):
        self.paku.logic(self, self.paku.location, self.paku.state)

        self.consume_cookie(self.paku.location)
        self.consume_pill(self.paku.location)

    def play_ghost(self, ghost):
        ghost.logic(self, ghost.location, ghost.state)

    def rehome_ghost(self, ghost):
        raise NotImplementedError()


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
