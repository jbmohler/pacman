import pmlib


class Music:
    def happy(self):
        raise NotImplementedError()

    def sad(self):
        raise NotImplementedError()

    def devastated(self):
        raise NotImplementedError()


def cli_render(board):
    raise NotImplementedError()


if __name__ == "__main__":
    board = pmlib.PacmanBoard()

    board.load_from_string(pmlib.level1)

    pmlib.play(board, cli_render, Music())
