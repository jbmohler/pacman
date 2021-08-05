# +-----------------------+
# |oooooo*ooooooooo*oooooo|
# oo+---------o---------+oo
# |o|o*ooooooooooooooo*o|o|
# |o+----o+-------+o----+o|
# |ooooooooooooooooooooooo|
# |o+----o|o+---+o|o----+o|
# |o|o*ooo|o|xxx|o|ooo*o|o|
# |o+o----+o+-x-+o+----o+o|
# |ooooooo|ooo@ooo|ooooooo|
# |o+----o+o-----o+o----+o|
# |o|o*ooooooooooooooo*o|o|
# oo+---------o---------+oo
# |oooooo*ooooooooo*oooooo|
# +-----------------------+


class Character:
    def __init__(self):
        self.location = None
        self.state = {}

        self.logic = None


class PacmanBoard:
    WIDTH = 11 * 25
    HEIGHT = 11 * 15

    CLOSE = 6

    #  Fickle, Chaser, Ambusher and Stupid
    #  Inky, Blinky, Pinky and Clyde

    def __init__(self):
        self.cookies = []
        self.pills = []

        self.retries = 3
        self.empowered = False

        self.paku = None
        self.ghosts = None

    def load_from_string(self, s):
        raise NotImplementedError()

    def is_cleared(self):
        return len(self.cookies) > 0

    @classmethod
    def is_close(cls, loc1, loc2):
        return abs(loc1.x - loc2.x) + abs(loc1.y - loc2.y) < cls.CLOSE

    def is_collided(self):
        ploc = self.paku.location
        return any(self.is_close(ploc, ghost.location) for ghost in self.ghosts)

    def play_paku(self):
        self.paku.logic(self, self.paku.state)

        self.consume_cookie(self.paku.location)
        self.consume_pill(self.paku.location)

    def play_ghost(self, ghost):
        ghost.logic(self, ghost.state)

    def rehome_ghost(self, ghost):
        raise NotImplementedError()


def play(board, render, music):
    while True:
        board.play_paku()
        for ghost in board.ghosts:
            board.play_ghost(ghost)

        if board.is_cleared():
            music.happy()
            return True

        if board.empowered:
            for ghost in board.ghosts:
                if board.is_close(board.paku.location, ghost.location):
                    board.rehome_ghost(ghost)

        if not board.empowered and board.is_collided():
            if board.retries > 0:
                music.sad()
                board.reset_characters()
                board.retries -= 1
            else:
                music.devastated()
                return False
