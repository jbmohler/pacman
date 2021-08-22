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


class Vector:
    def __init__(self, dx=None, dy=None):
        """
        >>> vec = Vector(1, 2)
        >>> vec.dx == vec[0]
        True
        >>> vec.dx
        1
        """
        self.dx = dx
        self.dy = dy

    def __repr__(self):
        return f"Vector({self.dx}, {self.dy})"

    def __len__(self):
        # we masquerade as a tuple
        return 2

    def __getitem__(self, index):
        assert type(index) is int and 0 <= index <= 1
        return self.dx if index == 0 else self.dy

    def manhattan(self):
        """
        Return the manhattan size (sum of legs of right triangle with
        hdypotenuse from origin to this point) rather than the distance from the
        origin.   It's simple and good enough and keeps ints as ints.

        >>> vec = Vector(1.5, 3.)
        >>> vec.manhattan()
        4.5
        >>> vec = Vector(1, 3)
        >>> vec.manhattan(), type(vec.manhattan())
        (4, int)
        """

        return abs(self.dx) + abs(self.dy)

    def is_perpendicular(self, other: "Vector") -> bool:
        pass  # TODO: implement

    def unit(self) -> "Vector":
        pass  # TODO: implement


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

    def __add__(self, other: Vector) -> "Location":
        """
        >>> l1 = Location(1, 2)
        >>> l2 = Location(3, 4)
        >>> l1 + (5, 6)
        Location(6, 8)
        >>> l1 + l2
        Location(4, 6)
        """

        return Location(self.x + other[0], self.y + other[1])

    def __sub__(self, other: "Location") -> Vector:
        return Location(self.x - other[0], self.y - other[1])

    def rounded(self) -> "Location":
        pass  # TODO: implement


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

    def iter_paths(self, prior, first, maxlen):
        """
        Iterate non-backtracking paths with no direct reversals.  Such paths
        may have loops.

        >>> simple = PacmanMap.from_str(SIMPLE_TEST)
        >>> paths = list(simple.iter_paths(simple.paku_location(), simple.paku_location() + (1, 0), 3))
        >>> paths[0]
        [Location, Location, Location]
        """

        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]

        path = [first]

        # terminate the recursion
        if maxlen <= 1:
            yield path
            return

        current = first

        def wrapped(off):
            if not 0 <= off.x < self.width:
                return Location(off.x % self.width, off.y)
            if not 0 <= off.y < self.height:
                return Location(off.x, off.y % self.height)
            return off

        def is_wall(loc):
            return self[loc] & (self.WALL | self.GATE) != 0

        def adjacent(loc):
            for d in dirs:
                yield wrapped(loc + d)

        def eligible(loc):
            nonlocal prior
            return not is_wall(loc) and loc != prior

        # Construct a path list until a branch
        while True:
            open_spots = [adj for adj in adjacent(current) if eligible(adj)]

            if len(open_spots) == 1:
                path.append(open_spots[0])
                prior = current
                current = open_spots[0]
                if len(path) >= maxlen:
                    yield path
                    break
            elif len(open_spots) == 0:
                # this is a dead end
                yield path
                break
            else:
                # iterate branch choices
                for spot in open_spots:
                    for pnext in self.iter_paths(current, spot, maxlen - len(path)):
                        yield path + pnext
                break
