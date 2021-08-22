import os
from PIL import Image, ImageDraw

ARTDIR = os.path.dirname(os.path.normpath(__file__))


class Colors:
    # https://htmlcolorcodes.com/color-chart/flat-design-color-chart/
    # (#239B56)
    WALL_HIGHLIGHTS = "#239B56"
    WALL_INSET = "#F7DC6F"
    WALL_MAIN = "#2ECC71"


class Dimn:
    CELL_WIDTH = 64
    WALL_MARGIN = 12
    WALL_HIGHLIGHTS = 3


def draw_wall_0000():
    img = Image.new("RGBA", (Dimn.CELL_WIDTH, Dimn.CELL_WIDTH), (0, 0, 0, 0))

    draw = ImageDraw.Draw(img)
    margin = Dimn.WALL_MARGIN
    draw.ellipse(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        outline=Colors.WALL_HIGHLIGHTS,
        width=Dimn.WALL_HIGHLIGHTS + 1,
    )
    margin = Dimn.WALL_MARGIN + 1 * Dimn.WALL_HIGHLIGHTS
    draw.ellipse(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        outline=Colors.WALL_INSET,
        width=2 * Dimn.WALL_HIGHLIGHTS + 1,
    )
    margin = Dimn.WALL_MARGIN + 3 * Dimn.WALL_HIGHLIGHTS
    draw.ellipse(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        outline=Colors.WALL_HIGHLIGHTS,
        width=Dimn.WALL_HIGHLIGHTS + 1,
    )
    margin = Dimn.WALL_MARGIN + 4 * Dimn.WALL_HIGHLIGHTS
    draw.ellipse(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        fill=Colors.WALL_MAIN,
        outline=Colors.WALL_MAIN,
        width=Dimn.WALL_HIGHLIGHTS + 1,
    )

    img.save(os.path.join(ARTDIR, "wall-0000.png"))


def draw_interior_arc_wall(img, start, end):
    draw = ImageDraw.Draw(img)
    margin = Dimn.WALL_MARGIN
    draw.arc(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        start,
        end,
        fill=Colors.WALL_HIGHLIGHTS,
        width=Dimn.WALL_HIGHLIGHTS + 1,
    )
    margin = Dimn.WALL_MARGIN + 1 * Dimn.WALL_HIGHLIGHTS
    draw.arc(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        start,
        end,
        fill=Colors.WALL_INSET,
        width=2 * Dimn.WALL_HIGHLIGHTS + 1,
    )
    margin = Dimn.WALL_MARGIN + 3 * Dimn.WALL_HIGHLIGHTS
    draw.arc(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        start,
        end,
        fill=Colors.WALL_HIGHLIGHTS,
        width=Dimn.WALL_HIGHLIGHTS + 1,
    )
    margin = Dimn.WALL_MARGIN + 4 * Dimn.WALL_HIGHLIGHTS
    draw.pieslice(
        [margin, margin, Dimn.CELL_WIDTH - margin, Dimn.CELL_WIDTH - margin],
        start,
        end,
        fill=Colors.WALL_MAIN,
        width=0,
    )


def draw_straight_wall(img, xy_swap, left, right):
    draw = ImageDraw.Draw(img)

    def paired(sym_margin, fill, width):
        margin = sym_margin
        draw.line(xy_swap([(left, margin), (right, margin)]), fill=fill, width=width)

        margin = Dimn.CELL_WIDTH - sym_margin
        draw.line(xy_swap([(left, margin), (right, margin)]), fill=fill, width=width)

    margin = Dimn.CELL_WIDTH / 2 - 0.5
    draw.line(
        xy_swap([(left, margin), (right, margin)]),
        fill=Colors.WALL_MAIN,
        width=Dimn.CELL_WIDTH - 2 * Dimn.WALL_MARGIN - 8 * Dimn.WALL_HIGHLIGHTS + 2,
    )

    paired(
        Dimn.WALL_MARGIN + 1.0, fill=Colors.WALL_HIGHLIGHTS, width=Dimn.WALL_HIGHLIGHTS
    )
    paired(
        Dimn.WALL_MARGIN + 1 * Dimn.WALL_HIGHLIGHTS + 2.5,
        fill=Colors.WALL_INSET,
        width=2 * Dimn.WALL_HIGHLIGHTS,
    )
    paired(
        Dimn.WALL_MARGIN + 3 * Dimn.WALL_HIGHLIGHTS + 1.0,
        fill=Colors.WALL_HIGHLIGHTS,
        width=Dimn.WALL_HIGHLIGHTS,
    )


def draw_hori_wall(img, left, right):
    def no_op_swap(pairs):
        return [(x, y) for x, y in pairs]

    draw_straight_wall(img, no_op_swap, left, right)


def draw_vert_wall(img, left, right):
    def swap_swap(pairs):
        return [(y, x) for x, y in pairs]

    draw_straight_wall(img, swap_swap, left, right)


def draw_wall_0101():
    img = Image.new("RGBA", (Dimn.CELL_WIDTH, Dimn.CELL_WIDTH), (0, 0, 0, 0))

    draw_hori_wall(img, 0, Dimn.CELL_WIDTH)

    img.save(os.path.join(ARTDIR, "wall-0101.png"))


def draw_wall_0100():
    img = Image.new("RGBA", (Dimn.CELL_WIDTH, Dimn.CELL_WIDTH), (0, 0, 0, 0))

    draw_interior_arc_wall(img, 90, 270)
    draw_hori_wall(img, Dimn.CELL_WIDTH / 2, Dimn.CELL_WIDTH)

    img.save(os.path.join(ARTDIR, "wall-0100.png"))


def draw_wall_0001():
    img = Image.new("RGBA", (Dimn.CELL_WIDTH, Dimn.CELL_WIDTH), (0, 0, 0, 0))

    draw_interior_arc_wall(img, 270, 90)
    draw_hori_wall(img, 0, Dimn.CELL_WIDTH / 2)

    img.save(os.path.join(ARTDIR, "wall-0001.png"))


def draw_wall_1010():
    img = Image.new("RGBA", (Dimn.CELL_WIDTH, Dimn.CELL_WIDTH), (0, 0, 0, 0))

    draw_vert_wall(img, 0, Dimn.CELL_WIDTH)

    img.save(os.path.join(ARTDIR, "wall-1010.png"))


def draw_wall_1000():
    img = Image.new("RGBA", (Dimn.CELL_WIDTH, Dimn.CELL_WIDTH), (0, 0, 0, 0))

    draw_interior_arc_wall(img, 0, 180)
    draw_vert_wall(img, 0, Dimn.CELL_WIDTH / 2)

    img.save(os.path.join(ARTDIR, "wall-1000.png"))


def draw_wall_0010():
    img = Image.new("RGBA", (Dimn.CELL_WIDTH, Dimn.CELL_WIDTH), (0, 0, 0, 0))

    draw_interior_arc_wall(img, 180, 360)
    draw_vert_wall(img, Dimn.CELL_WIDTH / 2, Dimn.CELL_WIDTH)

    img.save(os.path.join(ARTDIR, "wall-0010.png"))


if __name__ == "__main__":
    draw_wall_0000()
    draw_wall_0100()
    draw_wall_0001()
    draw_wall_0101()
    draw_wall_1000()
    draw_wall_0010()
    draw_wall_1010()
