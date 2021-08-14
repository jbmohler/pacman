import itertools

# Map strings -- default dimensions 15 x 25

LEVEL1 = """
+-----------------------+
|oooooo*ooooooooo*oooooo|
oo+---------o---------+oo
|o|o*ooooooooooooooo*o|o|
|o+----o+-------+o----+o|
|ooooooooooooooooooooooo|
|o+----o|o+---+o|o----+o|
|o|o*ooo|o|xxx|o|ooo*o|o|
|o+o----+o+-=-+o+----o+o|
|ooooooo|ooo@ooo|ooooooo|
|o+----o+o-----o+o----+o|
|o|o*ooooooooooooooo*o|o|
oo+---------o---------+oo
|oooooo*ooooooooo*oooooo|
+-----------------------+
"""

SIMPLE_TEST = """
+-------+
oooo*oooo
|o+---+o|
|o|xxx|o|
|o+-=-+o|
|ooo@ooo|
+-------+
"""


class MapParseError(Exception):
    pass


class PacmanMap:
    """
    >>> simple = PacmanMap.from_str(SIMPLE_TEST)
    >>> # a global invariant
    >>> simple[simple.paku_location()] == PacmanMap.PAKU
    True
    >>> simple.width, simple.height
    (9, 7)
    >>> simple.paku_location()
    (4, 5)
    >>> simple.ghost_locations()
    [(3, 3), (4, 3), (5, 3)]
    >>> simple.pill_locations()
    [(4, 1)]
    >>> len(simple.cookie_locations())
    20
    """

    DIR_MASK = 0x000F
    WALL = 0x0010
    GATE = 0x0020
    PILL = 0x0040
    COOKIE = 0x0080
    PAKU = 0x0100
    GHOST = 0x0200

    def __init__(self):
        # Grid will be a list interpreted as a 2 dim'l array.
        self.grid = None

        self.width = None
        self.height = None

    @classmethod
    def from_str(cls, s):
        lines = [ll.strip() for ll in s.split("\n") if ll.strip() != ""]

        if len(lines) == 0:
            raise MapParseError("no lines found")

        lengths = set([len(ll) for ll in lines])

        if len(lengths) > 1:
            raise MapParseError(f"map lines must be uniform length: ({lengths})")

        self = cls()

        self.width = lengths.pop()
        self.height = len(lines)

        def deserialize(ch):
            if ch in "|-+":
                return cls.WALL
            elif ch in "=":
                return cls.GATE
            elif ch in "o":
                return cls.COOKIE
            elif ch in "*":
                return cls.PILL
            elif ch in "@":
                return cls.PAKU
            elif ch in "x":
                return cls.GHOST
            else:
                raise MapParseError(f"unknown legend character {ch}")

        self.grid = [deserialize(ch) for line in lines for ch in line]

        # TODO: assert that every side exit must have a corresponding opposite entry.

        return self

    def __getitem__(self, index):
        assert len(index) == 2, f"index must be an integer 2-tuple: not {index}"

        # TODO :  is this really correct compared to the parser?
        return self.grid[index[0] * self.width + index[1]]

    def _iter_element(self, elt):
        for x, y in itertools.product(range(self.width), range(self.height)):
            if self[x, y] & elt:
                yield (x, y)

    def paku_location(self):
        pakus = list(self._iter_element(self.PAKU))
        assert len(pakus) == 1
        return pakus[0]

    def ghost_locations(self):
        return list(self._iter_element(self.GHOST))

    def pill_locations(self):
        return list(self._iter_element(self.PILL))

    def cookie_locations(self):
        return list(self._iter_element(self.COOKIE))
