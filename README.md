# Introduction

I write pacman ... because why not?

# Design

The `pmlib` directory is supposed to be a pure backend with virtually no front
end rendering assumptions.  It operates a grid with (presumed) square cells and
places paku and the ghosts with floating point coordinates on that grid.  It is
the responsibility of the front end to render these floating point locations
across cells as needed.

Each character takes a callable for the logic function which must return a
direction in which to travel.  The `pmlib` core moves the character one epsilon
move distance every game iteration.  The logic function takes a `state`
dictionary which allows the developer of the logic function to retain state
across iterations to have a longer term plan.

# Front ends

## Console

A proof-of-concept console rendering should be included.  It would be best
viewed in a square font such as https://strlen.com/square/ .

## Qt

QPainter in a QWidget.

## JSON websocket

Every render call sends out a (hopefully small?) updated board and this could
be passed to a JS front-end.  Render to HTML canvas.
